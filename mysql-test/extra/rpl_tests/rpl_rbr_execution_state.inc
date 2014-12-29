#
# SQL thread RBR execution state.
#

source include/master-slave.inc;
source include/have_binlog_format_row.inc;
source include/have_innodb.inc;

--echo #
--echo # Test locks rows to block a RBR delete rows event
--echo # so that the SQL thread state can be checked.
--echo #

--echo # connection: slave
connection slave;
SET GLOBAL innodb_lock_wait_timeout = 100;

--echo # connection: master
connection master;

CREATE TABLE t1 (a INT PRIMARY KEY, b INT);
INSERT INTO t1 VALUES (1,1),(2,2),(3,3),(4,4),(5,5);

sync_slave_with_master;

--echo # connection: slave
connection slave;

START TRANSACTION;
SELECT * FROM t1 WHERE a > 2 LOCK IN SHARE MODE;

--echo # connection: slave1
connection slave1;

START TRANSACTION;
SELECT * FROM t1 WHERE a > 4 LOCK IN SHARE MODE;

--echo # connection: master
connection master;

DELETE FROM t1 WHERE a > 2;

--echo # connection: slave
connection slave;

let $wait_condition=
  SELECT COUNT(*) = 1 FROM INFORMATION_SCHEMA.PROCESSLIST
  WHERE STATE LIKE "Executing Delete_rows event at position %";
--source include/wait_condition.inc


ROLLBACK;

--echo # connection: slave
connection slave;

let $wait_condition=
  SELECT COUNT(*) = 1 FROM INFORMATION_SCHEMA.PROCESSLIST WHERE STATE LIKE
  "Handling row % of 3 for a Delete_rows event on table `test`.`t1`";

--source include/wait_condition.inc

SET GLOBAL innodb_lock_wait_timeout = DEFAULT;

--echo # connection: slave
connection slave1;
ROLLBACK;

connection master;

DROP TABLE t1;

sync_slave_with_master;

--source include/rpl_end.inc
