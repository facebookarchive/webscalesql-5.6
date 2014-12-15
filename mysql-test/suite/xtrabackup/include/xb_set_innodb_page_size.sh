page_size_cnf="innodb_page_size=$1"
cnf_file="${MYSQLTEST_VARDIR}/my.cnf"
tmp_file="${MYSQL_TMP_DIR}/tmp.cnf"
cat $cnf_file | awk  -v page_size_cnf=$page_size_cnf '{print;} /\[mysqld\]/ {print page_size_cnf;}' > $tmp_file
mv $tmp_file $cnf_file
