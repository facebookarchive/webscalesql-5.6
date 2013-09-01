--require r/have_noprofiling.require
--disable_query_log
show variables like 'have_profiling';
--enable_query_log
