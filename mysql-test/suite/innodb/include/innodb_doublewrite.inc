# Embedded server does not support crashing
--source include/not_embedded.inc
--disable_warnings
DROP TABLE IF EXISTS t1;
DROP TABLE IF EXISTS t2;
--enable_warnings

let $data_dir = `SELECT @@datadir`;
let $page_size = `SELECT @@innodb_page_size`;
let $corrupt_exec = python suite/innodb/t/innodb_corrupt_doublewrite_pages.py $data_dir $page_size;

SET GLOBAL innodb_doublewrite=2;
CREATE TABLE t1(a INT PRIMARY KEY AUTO_INCREMENT, b char(255) default '') ENGINE=innodb;
INSERT INTO t1(a) VALUES(NULL);
INSERT INTO t1(a) SELECT NULL FROM t1;
INSERT INTO t1(a) SELECT NULL FROM t1;
INSERT INTO t1(a) SELECT NULL FROM t1;
INSERT INTO t1(a) SELECT NULL FROM t1;
INSERT INTO t1(a) SELECT NULL FROM t1;
INSERT INTO t1(a) SELECT NULL FROM t1;
INSERT INTO t1(a) SELECT NULL FROM t1;
INSERT INTO t1(a) SELECT NULL FROM t1;
INSERT INTO t1(a) SELECT NULL FROM t1;
INSERT INTO t1(a) SELECT NULL FROM t1;
INSERT INTO t1(a) SELECT NULL FROM t1;
INSERT INTO t1(a) SELECT NULL FROM t1;
INSERT INTO t1(a) SELECT NULL FROM t1;
connect(con1, localhost, root, , test, $MASTER_MYPORT, $MASTER_MYSOCK);
connection con1;
--send FLUSH TABLES t1

connection default;
--exec echo "wait" > $MYSQLTEST_VARDIR/tmp/mysqld.1.expect
--shutdown_server 10
--source include/wait_until_disconnected.inc

exec $corrupt_exec 2;

--enable_reconnect
# Write file to make mysql-test-run.pl start up the server again
--exec echo "restart" > $MYSQLTEST_VARDIR/tmp/mysqld.1.expect
--source include/wait_until_connected_again.inc
SET GLOBAL innodb_doublewrite=1;
CREATE TABLE t2(a INT PRIMARY KEY AUTO_INCREMENT, b char(255) default '') ENGINE=innodb;
INSERT INTO t2(a) VALUES(NULL);
INSERT INTO t2(a) SELECT NULL FROM t2;
INSERT INTO t2(a) SELECT NULL FROM t2;
INSERT INTO t2(a) SELECT NULL FROM t2;
INSERT INTO t2(a) SELECT NULL FROM t2;
INSERT INTO t2(a) SELECT NULL FROM t2;
INSERT INTO t2(a) SELECT NULL FROM t2;
INSERT INTO t2(a) SELECT NULL FROM t2;
INSERT INTO t2(a) SELECT NULL FROM t2;
INSERT INTO t2(a) SELECT NULL FROM t2;
INSERT INTO t2(a) SELECT NULL FROM t2;
INSERT INTO t2(a) SELECT NULL FROM t2;
INSERT INTO t2(a) SELECT NULL FROM t2;
INSERT INTO t2(a) SELECT NULL FROM t2;
connect(con2, localhost, root, , test, $MASTER_MYPORT, $MASTER_MYSOCK);
connection con2;
--send FLUSH TABLES t2
connection default;
--exec echo "wait" > $MYSQLTEST_VARDIR/tmp/mysqld.1.expect
--shutdown_server 10
--source include/wait_until_disconnected.inc

exec $corrupt_exec 1;
--enable_reconnect
# Write file to make mysql-test-run.pl start up the server again
--exec echo "restart" > $MYSQLTEST_VARDIR/tmp/mysqld.1.expect
--source include/wait_until_connected_again.inc

DROP TABLE t1;
DROP TABLE t2;
