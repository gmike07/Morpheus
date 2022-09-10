
# DO ONCE
# CREATE DATABASE puffer1;
# CREATE USER puffer1 WITH PASSWORD '<postgres password>';
# GRANT ALL PRIVILEGES ON DATABASE puffer1 TO puffer1;
# \q

echo '======================================'
echo enter the following commands:
echo '1. sudo -u postgres psql'
echo '2. CREATE DATABASE puffer1;'
echo "3. CREATE USER puffer1 WITH PASSWORD \'<postgres password>\';"
echo '4. GRANT ALL PRIVILEGES ON DATABASE puffer1 TO puffer1;'
echo '5. \\q'
echo '======================================'

# influx
# CREATE USER puffer WITH PASSWORD '<influxdb password>' WITH ALL PRIVILEGES
#TODO: Next, modify /etc/influxdb/influxdb.conf to enable authentication by setting the auth-enabled option to true in the [http] section
echo 'TODO: Next, modify /etc/influxdb/influxdb.conf to enable authentication by setting the auth-enabled option to true in the [http] section'
echo '======================================'
echo enter the following commands:
echo 1. sudo systemctl restart influxdb
echo 2. influx
echo 3. auth
echo 4. username: puffer1
echo 5. "password: <influxdb password>"
echo 6. "CREATE DATABASE puffer1"
echo 7. "SHOW DATABASES"
echo 8. "exit"
echo '======================================'
