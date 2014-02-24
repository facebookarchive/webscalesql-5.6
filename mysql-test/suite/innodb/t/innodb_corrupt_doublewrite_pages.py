import sys, glob, random, os, threading, subprocess, re, time

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

def fil_page_get_type(page):
       return mach_read_from_2(page[FIL_PAGE_TYPE:])

def get_dblwr_page_nos(page, block1, block2):
  if fil_page_get_type(page) == FIL_PAGE_TYPE_DBLWR_HEADER:
    ptr = page[FIL_PAGE_DATA:]
    num_pages = mach_read_from_2(ptr)
    ptr = ptr[2:]
    for i in xrange(num_pages):
      space_id = mach_read_from_4(ptr)
      ptr = ptr[4:]
      page_no = mach_read_from_4(ptr)
      ptr = ptr[4:]
      if space_id:
        yield space_id, page_no
  else:
    for i in xrange(TRX_SYS_DOUBLEWRITE_BLOCK_SIZE * 2):
      page_no = mach_read_from_4(page[FIL_PAGE_OFFSET:])
      space_id = mach_read_from_4(page[FIL_PAGE_ARCH_LOG_NO_OR_SPACE_ID:])
      if space_id:
        yield space_id, page_no
      page = page[UNIV_PAGE_SIZE:]

def get_ibd_map(data_dir):
  arr = glob.glob('%s/*/*.ibd' % data_dir)
  m = {}
  for path in arr:
    f = open(path, 'rb')
    space_id = mach_read_from_4(f.read(4096)[FIL_PAGE_ARCH_LOG_NO_OR_SPACE_ID:])
    m[space_id] = path
  return m

def corrupt_random_page(pages_in_dblwr, ibd_map):
  space_id, page_no = random.choice([p for p in pages_in_dblwr])
  #print "corrupting space_id=%d, page_no=%d" % (space_id, page_no)
  table_file = ibd_map[space_id]
  f = open(table_file, 'r+b')
  # seek to a random offset with in the page.
  f.seek(UNIV_PAGE_SIZE * page_no)
  page = f.read(UNIV_PAGE_SIZE)
  offset = random.randint(256, 768)
  new_page = page[:offset] + \
             chr(ord(page[offset]) ^ 1) + \
             page[offset + 1:]
  f.seek(UNIV_PAGE_SIZE * page_no)
  f.write(new_page)
  f.flush()
  os.fsync(f.fileno())
  f.close()
  return space_id, page_no, page

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
      self.process = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE)
      self.process.communicate()
    thread = threading.Thread(target=target)
    thread.start()
    thread.join(self.timeout)
    if thread.is_alive():
      self.process.terminate()
    return self.process.returncode

def main():
  if len(sys.argv) < 4:
    raise Exception('You must specify the path for the data directory of the server and the doublewrite mode')
    exit(1)
  data_dir = sys.argv[1]
  global UNIV_PAGE_SIZE
  global TRX_SYS_PAGE_NO
  global TRX_SYS_DOUBLEWRITE
  global TRX_SYS_DOUBLEWRITE_MAGIC_N
  global FSEG_HEADER_SIZE
  global TRX_SYS_DOUBLEWRITE_MAGIC
  global TRX_SYS_DOUBLEWRITE_BLOCK1
  global TRX_SYS_DOUBLEWRITE_BLOCK2
  global TRX_SYS_DOUBLEWRITE_BLOCK_SIZE
  global FIL_PAGE_TYPE_DBLWR_HEADER
  global FIL_PAGE_TYPE
  global FIL_PAGE_DATA
  global FIL_PAGE_OFFSET
  global FIL_PAGE_ARCH_LOG_NO_OR_SPACE_ID

  UNIV_PAGE_SIZE = int(sys.argv[2])
  TRX_SYS_PAGE_NO = 5
  TRX_SYS_DOUBLEWRITE = (UNIV_PAGE_SIZE - 200)
  TRX_SYS_DOUBLEWRITE_MAGIC_N = 536853855
  FSEG_HEADER_SIZE  = 10
  TRX_SYS_DOUBLEWRITE_MAGIC = FSEG_HEADER_SIZE
  TRX_SYS_DOUBLEWRITE_BLOCK1 = 4 + FSEG_HEADER_SIZE
  TRX_SYS_DOUBLEWRITE_BLOCK2  = 8 + FSEG_HEADER_SIZE
  TRX_SYS_DOUBLEWRITE_BLOCK_SIZE = 1048576 / UNIV_PAGE_SIZE
  FIL_PAGE_TYPE_DBLWR_HEADER = 13
  FIL_PAGE_TYPE = 24
  FIL_PAGE_DATA = 38
  FIL_PAGE_OFFSET = 4
  FIL_PAGE_ARCH_LOG_NO_OR_SPACE_ID = 34
  DBLWR_FAIL_MESSAGE = "InnoDB: Cannot recover it from the doublewrite buffer because it was written in reduced-doublewrite mode.\n"
  DBLWR_FAIL0_MESSAGE = "InnoDB: Doublewrite does not have page_no=0 of space: "
  DBLWR_SUCCESS_MESSAGE = "InnoDB: Trying to recover it from the doublewrite buffer.\n"
  DBLWR_SUCCESS0_MESSAGE = "InnoDB: Restoring page 0 of tablespace "

  innodb_doublewrite = int(sys.argv[3])
  if innodb_doublewrite != 1 and innodb_doublewrite != 2:
    raise Exception("innodb_doublewrite must be 1 or 2 for this test.")
    exit(1)
  log_file = '%s/innodb_corrupt_doublewrite-%d.log'  % (os.environ['MYSQL_TMP_DIR'], innodb_doublewrite)
  mysqld_cmd = os.environ['MYSQLD_CMD'].replace('--core-file', '')
  mysqld_cmd += ' --log_error=%s'  % log_file
  ibd_map = get_ibd_map(data_dir)
  ibdata_path = '%s/ibdata1' % data_dir
  f = open(ibdata_path, 'rb')
  doublewrite = get_doublewrite(f)
  block1 = mach_read_from_4(doublewrite[TRX_SYS_DOUBLEWRITE_BLOCK1:])
  block2 = mach_read_from_4(doublewrite[TRX_SYS_DOUBLEWRITE_BLOCK2:])
  f.seek(block1 * UNIV_PAGE_SIZE)
  buf1 = f.read(TRX_SYS_DOUBLEWRITE_BLOCK_SIZE * UNIV_PAGE_SIZE)
  f.seek(block2 * UNIV_PAGE_SIZE)
  buf2 = f.read(TRX_SYS_DOUBLEWRITE_BLOCK_SIZE * UNIV_PAGE_SIZE)
  space_id, page_no, page = corrupt_random_page(get_dblwr_page_nos(buf1 + buf2, block1, block2), ibd_map)
  # start the server, the server must not be able to start if reduced-doublewrite mode
  # was used.
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

