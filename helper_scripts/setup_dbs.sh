
# DO ONCE
# CREATE DATABASE puffer1;
# CREATE USER puffer1 WITH PASSWORD '<postgres password>';
# GRANT ALL PRIVILEGES ON DATABASE puffer1 TO puffer1;
# \q

# echo '======================================'
# echo enter the following commands:
# echo '1. sudo -u postgres psql'
# echo '2. CREATE DATABASE puffer1;'
# echo "3. CREATE USER puffer1 WITH PASSWORD \'<postgres password>\'; (in my case '1')"
# echo '4. GRANT ALL PRIVILEGES ON DATABASE puffer1 TO puffer1;'
# echo '5. \\q'
# echo '======================================'

sudo su postgres <<EOF
createdb  puffer1;
psql -c "CREATE USER puffer1 WITH PASSWORD '1';"
psql -c "grant all privileges on database puffer1 to puffer1;"
echo "Postgres User 'puffer1' and database 'puffer1' created."
EOF

# influx
# CREATE USER puffer WITH PASSWORD '<influxdb password>' WITH ALL PRIVILEGES
#TODO: Next, modify /etc/influxdb/influxdb.conf to enable authentication by setting the auth-enabled option to true in the [http] section
echo 'TODO: Next, modify /etc/influxdb/influxdb.conf to enable authentication by setting the auth-enabled option to true in the [http] section'
echo '======================================'
echo enter the following commands:
echo 1. sudo systemctl restart influxdb
echo 2. influx
echo "3. create user \"puffer1\" with password ‘<influxdb password>’ with all privileges (in my case '1')"
echo 4. auth
echo 5. username: puffer1
echo 6. "password: <influxdb password> (in my case 1)"
echo 7. "CREATE DATABASE puffer1"
echo 8. "SHOW DATABASES"
echo 9. "exit"
echo '======================================'
