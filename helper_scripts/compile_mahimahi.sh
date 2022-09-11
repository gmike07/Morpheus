#!/bin/bash
cd ..
cd mahimahi
sudo apt install dnsmasq -y
sudo apt-get install iptables -y
sudo apt-get install protobuf-compiler -y
# download protobuf
sudo apt-get install autoconf automake libtool curl make g++ unzip -y
wget https://github.com/protocolbuffers/protobuf/releases/download/v3.6.1/protobuf-all-3.6.1.tar.gz
tar -xvf protobuf-all-3.6.1.tar.gz
rm protobuf-all-3.6.1.tar.gz
cd protobuf-3.6.1
sudo ./autogen.sh && sudo ./configure && sudo make

make check
sudo make install
which protoc
sudo ldconfig
cd ..

sudo apt install apache2-dev -y
sudo apt install xcb -y
sudo apt-get install libx11-dev -y
sudo apt-get install libxcb-xrm-dev -y 
sudo apt-get install libxcb-present-dev -y
sudo apt-get install -y libsdl-pango-dev -y 
sudo apt install git-buildpackage -y
sudo apt autoremove
sudo ./autogen.sh
sudo ./configure
cd src
sudo make
cd frontend
for file in *; do
	if [[ -x "$file" ]]
	then
            sudo chown root:root $file
	    sudo chmod 4755 $file
	fi
done
cd ..
cd ..
cd ..
