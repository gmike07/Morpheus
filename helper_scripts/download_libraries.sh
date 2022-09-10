cd ..
cd ..
mv Morpheus/ puffer/
cd puffer
# git branch -a
# git checkout amazon_congestion_control
git submodule sync --recursive
git submodule update --recursive --init

sudo apt-get update -qq
cwd=$(pwd)
sudo apt-get install -y xmlto libboost-all-dev aptitude
aptitude search boost
# sudo systemctl disable systemd-resolved
# sudo systemctl stop systemd-resolved
# sudo unlink /etc/resolv.conf
sudo apt-get install -y -q gcc-7 g++-7 libmpeg2-4-dev libpq-dev \
                          libssl-dev libcrypto++-dev libyaml-cpp-dev \
                          libboost-dev liba52-dev opus-tools libopus-dev \
                          libsndfile-dev libavformat-dev libavutil-dev ffmpeg \
                          git automake libtool python python3 cmake wget chromium-browser unzip apache2
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-7 99
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-7 99
sudo apt-get install -y pkg-config libcurlpp-dev libcurl4-openssl-dev
sudo apt install python3-pip -y
sudo apt install python3 -y
pip3 install django psycopg2-binary influxdb pyyaml matplotlib flask tqdm
pip3 install django[argon2]
sudo apt install postgresql -y

wget -qO- https://repos.influxdata.com/influxdb.key | sudo apt-key add -
source /etc/lsb-release
echo "deb https://repos.influxdata.com/${DISTRIB_ID,,} ${DISTRIB_CODENAME} stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
sudo apt-get update -y && sudo apt-get install influxdb -y
sudo systemctl unmask influxdb.service
sudo systemctl start influxdb

sudo apt install -y mahimahi
sudo apt remove -y mahimahi

git clone https://github.com/jtv/libpqxx.git
cd libpqxx && git checkout 7.3.0 && sudo ./configure --enable-documentation=no && sudo make -j3 install
sudo useradd --create-home --shell /bin/bash user
sudo cp -R . /home/user/puffer
sudo chown ubuntu -R /home/user/puffer # machine home name
cd ..

cd third_party/
wget https://github.com/StanfordSNR/pytorch/releases/download/v1.0.0-puffer/libtorch.tar.gz
tar -xvf libtorch.tar.gz
rm libtorch.tar.gz
# export PATH="$cwd:$PATH"
# source ~/.bashrc
cd ..
cd third_party/
rm -rf libwebm.fork/
mv libwebm_2.fork/ libwebm.fork/
cd ..
cd helper_scripts
