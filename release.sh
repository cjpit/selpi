#bin/bash
docker-compose down
rm -rf /usr/share/nginx/html
cp -R pwa/dist/pwa/* /usr/share/nginx/html/
docker-compose build
docker-compose up -d
sudo systemctl reload nginx