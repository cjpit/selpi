#bin/bash
docker compose down
sudo rm -rf /var/www/selpi.cjpit.com/html/*
sudo cp -R /home/pi/dev/selpi/pwa/dist/pwa/* /var/www/selpi.cjpit.com/html
sudo chown -R www-data:www-data  /var/www/selpi.cjpit.com/html
docker compose build
docker compose up -d
sudo systemctl reload nginx

