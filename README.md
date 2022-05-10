# Puffer [![Build Status](https://travis-ci.org/StanfordSNR/puffer.svg?branch=master)](https://travis-ci.org/StanfordSNR/puffer)

# First things to set up
- Follow the wiki from the github repo of puffer  
- install libcurl4-openssl-dev, libcurlpp-dev
- install Pillow before installing tf-agents,tensorflow

## Prerequisites
1. validate cc: bbr and cubic and vegas are available with `sysctl net.ipv4.tcp_available_congestion_control`
2. If not, add bbr and vefas:
    - edit the file: `sudo vi /etc/sysctl.conf`
    - add the lines:
        ```
        net.core.default_qdisc=fq
        net.ipv4.tcp_congestion_control=vegas
        net.ipv4.tcp_congestion_control=bbr
        ```
    - restart: `sudo sysctl --system`'
4. fix ports in `src/portal/puffer/static/puffer/js/puffer.js` the argument that determine `ws_host_port`
5. edit in `./helper_scripts/settings.yml` the variables:
    - `media_dir` - from where videos are served
    - `log_dir` - log dir
    - `experiments` - experiments to run
6. you can view videos http://localhost:8080/player/{?wsport=9361}

## FCC dataset
Generate traces with:
* `cd traces`
* `python load_webget_data.py`
* `python3 convert_mahimahi_format.py`
* `python3 generate_train_test_traces.py`

# How to run experiments?
0. run `./run_emulation.sh --clients <num clients> -m <model, num epochs to train>*`.

## Debug
- Remember to compile with the flag `-g`: `sudo make -j CXXFLAGS='-DNONSECURE -g' CFLAGS='-g'`
- export env variable: `source ~/.bashrc`  
- Debugging the server: `./src/media-server/ws_media_server src/settings.yml 1 3`  

# InfluxDB
Data is collected from the streaming and written to influxdb.  
- influx paths:
    - data: `/var/lib/influxdb`
    - config: `/etc/influxdb/influxdb.conf`
- Useful commands:  
    - start db: `sudo systemctl start influxdb`  
    - `show databases`  
    - `use puffer`  
    - `show measurements`  
    - `select * from measurements`
    - set UTC: `precision rfc3339`
    - delete all measurements `drop series from /.*/`
    - delete by id: `delete from video_acked where expt_id='36'`
    - `delete from active_streams, client_buffer, client_sysinfo, video_acked, video_sent where expt_id='180'`

# Postgress
psotgress quick guide:
* connect:
	- `psql "host=127.0.0.1 port=5432 dbname=puffer user=puffer password=$PUFFER_PORTAL_DB_KEY"`
	- `psql "host=127.0.0.1 port=5432 dbname=puffer user=puffer password=123456"`
* exit: `\q`
* use db: `use puffer`
* show tables: `\dt`
* execute commands: `SELECT * FROM puffer_experiment;` (note for the semicolon)
* delete: `DELETE FROM puffer_experiment;`

# Testing models
0. run `./run_emulation.sh --clients <num clients> -m <model, num epochs to train>* -ts`.