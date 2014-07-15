#
# Copyright (c) 2013, Oracle and/or its affiliates. All rights reserved.
#
--let $include_filename= install_semisync.inc
--source include/begin_include_file.inc

--source include/not_embedded.inc
--source include/have_semisync.inc

--connection master

--disable_query_log
SET GLOBAL rpl_semi_sync_master_enabled = 1;

--connection slave
--source include/stop_slave_io.inc
SET GLOBAL rpl_semi_sync_slave_enabled = 1;
--source include/start_slave_io.inc
--enable_query_log

--source include/end_include_file.inc
