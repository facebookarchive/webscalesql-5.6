#ifndef _blind_fwrite_h
#define _blind_fwrite_h

#include <my_global.h>
#include <my_dbug.h>

static inline void
blind_fwrite(const void *ptr, size_t size, size_t num, FILE *stream)
{
  if (fwrite(ptr, size, num, stream) != num)
  {
    DBUG_PRINT("error",("Error in blind_fwrite. Should have been looking."));
    DBUG_ABORT();
  }
}

#endif // _blind_fwrite_h
