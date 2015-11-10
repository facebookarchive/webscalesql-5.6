import sys, glob, random, os, threading, subprocess, re, time, zlib

def get_doublewrite(f):
  f.seek(TRX_SYS_PAGE_NO * UNIV_PAGE_SIZE)
  page = f.read(UNIV_PAGE_SIZE)
  doublewrite = page[TRX_SYS_DOUBLEWRITE:]
  if mach_read_from_4(doublewrite[TRX_SYS_DOUBLEWRITE_MAGIC:]) != TRX_SYS_DOUBLEWRITE_MAGIC_N:
    raise Exception('Doublewrite buffer is not created on the ibd file. Something is wrong.')
    exit(1)
  return doublewrite

def mach_read_from_4(b):
  return (ord(b[0]) << 24) | (ord(b[1]) << 16) | (ord(b[2]) << 8) | ord(b[3])

def mach_read_from_2(b):
  return (ord(b[0]) << 8) | ord(b[1])

def mach_write_to_4(f, val):
  f.write(chr((val >> 24) & 0xff) +
          chr((val >> 16) & 0xff) +
          chr((val >> 8) & 0xff) +
          chr(val &0xff))

def mach_write_to_2(f, val):
  f.write(chr((val >> 8) & 0xff) +
          chr(val &0xff))

def get_ibd_map(data_dir):
  arr = glob.glob('%s/*/*.ibd' % data_dir)
  m = {}
  for path in arr:
    with open(path, 'rb') as f:
      space_id = mach_read_from_4(
        f.read(4096)[FIL_PAGE_ARCH_LOG_NO_OR_SPACE_ID:])
    m[space_id] = path
  m[0] = '%s/ibdata1' % data_dir
  return m

def corrupt_page_no(ibd_map, space_id, page_no):
  table_file_path = ibd_map[space_id]
  with open(table_file_path, 'r+b') as table_file:
    # Read the existing page
    table_file.seek(UNIV_PAGE_SIZE * page_no)
    page = table_file.read(UNIV_PAGE_SIZE)
    # Corrupt a byte somewhere in the middle of the page
    offset = random.randint(256, 768)
    new_page = page[:offset] + \
               chr(ord(page[offset]) ^ 1) + \
               page[offset + 1:]
    # Write the corrupted page
    table_file.seek(UNIV_PAGE_SIZE * page_no)
    table_file.write(new_page)
    table_file.flush()
    os.fsync(table_file.fileno())
    return page

class WrongDblwrModeError(Exception):
  pass

def update_header_checksum(ibdata_file, block1):
  # Read the updated header.
  ibdata_file.seek(block1 * UNIV_PAGE_SIZE)
  header = ibdata_file.read(BUF_DBLWR_HEADER_SIZE)
  # Compute the checksum as page_zip_calc_checksum would.
  checksum = zlib.adler32(header[FIL_PAGE_OFFSET:FIL_PAGE_LSN], 0)
  checksum = zlib.adler32(header[FIL_PAGE_TYPE:FIL_PAGE_TYPE+2], checksum)
  checksum = zlib.adler32(header[FIL_PAGE_ARCH_LOG_NO_OR_SPACE_ID:], checksum)
  # Write new checksum back to the file.
  ibdata_file.seek((block1 * UNIV_PAGE_SIZE) + FIL_PAGE_SPACE_OR_CHKSUM)
  mach_write_to_4(ibdata_file, checksum)

def write_page_to_dblwr(ibd_map, space_id, page_no, page, innodb_doublewrite):
  with open(ibd_map[0], 'r+b') as ibdata_file:
    doublewrite = get_doublewrite(ibdata_file)
    # Get the page number of the first doublewrite block.
    block1 = mach_read_from_4(doublewrite[TRX_SYS_DOUBLEWRITE_BLOCK1:])
    # Seek to the start of the first block.
    ibdata_file.seek(block1 * UNIV_PAGE_SIZE)
    # Seek to the page type.
    ibdata_file.seek(FIL_PAGE_TYPE, 1)
    # Read the raw bytes.
    page_type_raw = ibdata_file.read(2)
    # Check the mode of the doublewrite buffer.
    if mach_read_from_2(page_type_raw) == FIL_PAGE_TYPE_DBLWR_HEADER:
      # If we're reading a header page, we should be testing reduced
      # doublewrite mode.
      if not innodb_doublewrite == 2:
        raise WrongDblwrModeError('Found header in full mode.')

      # Relative seek to the page data.
      ibdata_file.seek(FIL_PAGE_DATA - FIL_PAGE_TYPE - 2, 1)

      # Update the number of pages in the buffer if it is zero.
      num_pages_raw = ibdata_file.read(2)
      if not mach_read_from_2(num_pages_raw):
        ibdata_file.seek(-2, 1)
        mach_write_to_2(ibdata_file, 1)

      # Insert our space_id, page_no as the first list entry.
      mach_write_to_4(ibdata_file, space_id)
      mach_write_to_4(ibdata_file, page_no)

      update_header_checksum(ibdata_file, block1)
    else:
      # If we're not reading a header page, we should be testing full
      # doublewrite mode.
      if not innodb_doublewrite == 1:
        raise WrongDblwrModeError('Missing header in reduced mode.')

      # Just write the passed in page to the first page of the first block.
      ibdata_file.seek(block1 * UNIV_PAGE_SIZE)
      ibdata_file.write(page)

    # Ensure changes hit disk.
    ibdata_file.flush()
    os.fsync(ibdata_file.fileno())

def corrupt_page(ibd_map, space_id, innodb_doublewrite):
    # Arbitrarily picking to corrupt page 5.
    page_no = 5
    # Corrupt the page in the target space_id.
    page = corrupt_page_no(ibd_map, space_id, page_no)
    # Put the corrupted page in the doublewrite buffer.
    write_page_to_dblwr(ibd_map, space_id, page_no, page, innodb_doublewrite)
    return page_no, page

def uncorrupt_page(space_id, page_no, page, ibd_map):
    f = open(ibd_map[space_id], 'r+b')
    f.seek(UNIV_PAGE_SIZE * page_no)
    f.write(page)
    f.flush()
    os.fsync(f.fileno())
    f.close()

class Command(object):
  def __init__(self, cmd, timeout):
    self.cmd = cmd
    self.process = None
    self.timeout = timeout
  def run(self):
    def target():
      args = filter(None, self.cmd.split(" "))
      self.process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE)
      self.process.communicate()
    thread = threading.Thread(target=target)
    thread.start()
    thread.join(self.timeout)
    if thread.is_alive():
      self.process.terminate()
    return self.process.returncode

def main():
  if len(sys.argv) < 5:
    raise Exception('Incorrect number of arguments.')
    exit(1)
  data_dir = sys.argv[1]
  global BUF_DBLWR_HEADER_SIZE
  global UNIV_PAGE_SIZE
  global TRX_SYS_PAGE_NO
  global TRX_SYS_DOUBLEWRITE
  global TRX_SYS_DOUBLEWRITE_MAGIC_N
  global FSEG_HEADER_SIZE
  global TRX_SYS_DOUBLEWRITE_MAGIC
  global TRX_SYS_DOUBLEWRITE_BLOCK1
  global FIL_PAGE_TYPE_DBLWR_HEADER
  global FIL_PAGE_TYPE
  global FIL_PAGE_DATA
  global FIL_PAGE_OFFSET
  global FIL_PAGE_LSN
  global FIL_PAGE_ARCH_LOG_NO_OR_SPACE_ID
  global FIL_PAGE_SPACE_OR_CHKSUM

  BUF_DBLWR_HEADER_SIZE = 4096
  UNIV_PAGE_SIZE = int(sys.argv[2])
  TRX_SYS_PAGE_NO = 5
  TRX_SYS_DOUBLEWRITE = (UNIV_PAGE_SIZE - 200)
  TRX_SYS_DOUBLEWRITE_MAGIC_N = 536853855
  FSEG_HEADER_SIZE  = 10
  TRX_SYS_DOUBLEWRITE_MAGIC = FSEG_HEADER_SIZE
  TRX_SYS_DOUBLEWRITE_BLOCK1 = 4 + FSEG_HEADER_SIZE
  FIL_PAGE_TYPE_DBLWR_HEADER = 13
  FIL_PAGE_TYPE = 24
  FIL_PAGE_DATA = 38
  FIL_PAGE_OFFSET = 4
  FIL_PAGE_LSN = 16
  FIL_PAGE_ARCH_LOG_NO_OR_SPACE_ID = 34
  FIL_PAGE_SPACE_OR_CHKSUM = 0
  DBLWR_FAIL_MESSAGE = "InnoDB: Cannot recover it from the doublewrite buffer because it was written in reduced-doublewrite mode.\n"
  DBLWR_FAIL0_MESSAGE = "InnoDB: Doublewrite does not have page_no=0 of space: "
  DBLWR_SUCCESS_MESSAGE = "InnoDB: Trying to recover it from the doublewrite buffer.\n"
  DBLWR_SUCCESS0_MESSAGE = "InnoDB: Restoring page 0 of tablespace "

  space_id = int(sys.argv[3])
  innodb_doublewrite = int(sys.argv[4])
  if innodb_doublewrite != 1 and innodb_doublewrite != 2:
    raise Exception("innodb_doublewrite must be 1 or 2 for this test.")
    exit(1)
  log_file = '%s/innodb_corrupt_doublewrite-%d.log'  % (os.environ['MYSQL_TMP_DIR'], innodb_doublewrite)
  mysqld_cmd = os.environ['MYSQLD_CMD'].replace('--core-file', '')
  mysqld_cmd += ' --log_error=%s'  % log_file

  ibd_map = get_ibd_map(data_dir)
  page_no, page = corrupt_page(ibd_map, space_id, innodb_doublewrite)

  # start the server, the server must not be able to start if
  # reduced-doublewrite mode was used.
  cmd = Command(mysqld_cmd, 30)
  ret = cmd.run()
  #print "cmd returned ", ret
  if innodb_doublewrite == 1:
    contents = open(log_file).read()
    if ret is not None:
      print contents
      raise Exception('MySQL failed to recover in full doublewrite mode.')
      exit(1)
    #Check here that the data page was indeed restored from the doublewrite buffer
    ind = contents.find(DBLWR_SUCCESS_MESSAGE)
    if ind == -1:
      ind = contents.find(DBLWR_SUCCESS0_MESSAGE)
      if ind == -1:
        print contents
        raise Exception('Doublewrite buffer was not used even though the following page was corrupt space_id=%d page_no=%d (doublewrite=1)'  % (space_id, page_no))
        exit(1)
    print DBLWR_SUCCESS_MESSAGE
  if innodb_doublewrite == 2:
    contents = open(log_file).read()
    if ret is None:
      print contents
      raise Exception('MySQL did not fail to recover even though reduced durability was used, and the following page was corrupt space_id=%d page_no=%d' % (space_id, page_no))
      exit(1)
    ind = contents.find(DBLWR_FAIL_MESSAGE)
    if ind == -1:
      ind = contents.find(DBLWR_FAIL0_MESSAGE)
      if ind == -1:
        print contents
        raise Exception('Doublewrite did not fail to recover as expected on space_id=%d page_no=%d (doublewrite=2)'  % (space_id, page_no))
        exit(1)
    print DBLWR_FAIL_MESSAGE
    # undo the change to the page.
    uncorrupt_page(space_id, page_no, page, ibd_map)

if __name__ == '__main__':
  main()

