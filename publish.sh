#/bin/bash
cd /selpi/pwa
yarn install
quasar build -m pwa -d
rm -rf /selpi/pwa/node_modules
scp -r /selpi/ pi@192.168.2.10:/home/pi/dev