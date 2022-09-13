#export PUFFER_PORTAL_SECRET_KEY='1'
#. ~/.bashrc
#export INFLUXDB_PASSWORD='1'
#. ~/.bashrc
#export PUFFER_PORTAL_DB_KEY='1'
#. ~/.bashrc
#pwd
# ./src/portal/manage.py migrate
# ln -s ../../../../../third_party/dist-for-puffer/ src/portal/puffer/static/puffer/dist

sudo env "PUFFER_PORTAL_SECRET_KEY=1" "INFLUXDB_PASSWORD=1" "PUFFER_PORTAL_DB_KEY=1" ./src/portal/manage.py runserver 0:$1
# ./src/portal/manage.py runserver 0:8080

