#
# Copyright (c) 2013, Oracle and/or its affiliates. All rights reserved.
#
--let $include_filename= uninstall_semisync.inc
--source include/begin_include_file.inc

--disable_query_log
--connection slave
--source include/stop_slave_io.inc

SET GLOBAL rpl_semi_sync_slave_enabled = 0;

--connection master
SET GLOBAL rpl_semi_sync_master_enabled = 0;
SET GLOBAL rpl_semi_sync_master_timeout = DEFAULT;

--connection slave
--source include/start_slave_io.inc
--enable_query_log

--source include/end_include_file.inc
