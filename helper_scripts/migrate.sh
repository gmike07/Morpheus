cd ..
env "PUFFER_PORTAL_SECRET_KEY=1" "INFLUXDB_PASSWORD=1" "PUFFER_PORTAL_DB_KEY=1" ./src/portal/manage.py migrate
# ./src/portal/manage.py migrate
ln -s ../../../../../third_party/dist-for-puffer/ src/portal/puffer/static/puffer/dist
env "PUFFER_PORTAL_SECRET_KEY=1" "INFLUXDB_PASSWORD=1" "PUFFER_PORTAL_DB_KEY=1" ./src/portal/manage.py runserver 0:$1

# sudo ./src/portal/manage.py runserver 0:80
cd helper_scripts
