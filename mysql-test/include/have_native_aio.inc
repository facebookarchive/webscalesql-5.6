--disable_query_log
if (`select @@global.innodb_use_native_aio != 1`)
{
  --skip native AIO is not in use
}
--enable_query_log
