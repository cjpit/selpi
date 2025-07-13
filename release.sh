#bin/bash
docker compose down
sudo rm -rf /usr/share/nginx/html
export NODE_OPTIONS=--openssl-legacy-provider
cd pwa
yarn install
quasar build -m pwa -d
cd dist/pwa
sudo rsync -R --recursive * /var/www/selpi.cjpit.com/html --exclude node_modules
sudo chown -R www-data:www-data /var/www/selpi.cjpit.com/html
cd ../../..
docker compose build
docker compose up -d
sudo systemctl reload nginx