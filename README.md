# Web Keylogger

sslsplit
========

[SSLsplit][1] is a tool for man-in-the-middle attacks against SSL/TLS encrypted
network connections.

## docker-compose.yml
* modify to suite your environment

## Server Setup

```bash
$ mkdir -p data/{key,log}
$ vim docker-compose.yml # modify env variables to reflect your environment
$ openssl req -x509 -newkey rsa:2048 -nodes -keyout data/key/ca.key -out data/key/ca.crt -days 3650 -subj '/CN=EasyPi'
$ docker-compose up -d
```

```bash
# setup
sysctl -w net.ipv4.ip_forward=1
iptables -t nat -N SSLSPLIT
iptables -t nat -A SSLSPLIT -p tcp --dport 80 -j REDIRECT --to-ports 8080
iptables -t nat -A SSLSPLIT -p tcp --dport 443 -j REDIRECT --to-ports 8443

# enable
iptables -t nat -A PREROUTING -j SSLSPLIT

# disable
iptables -t nat -D PREROUTING -j SSLSPLIT
```

## Client Setup

```bash
# ip route del to default via XXX.XXX.XXX.XXX
# ip route add default via YYY.YYY.YYY.YY

curl -k https://www.baidu.com/s?wd=hello+world
```

> ProTip: No warning dialog after importing `ca.crt` into system/browser.

## read more

- <https://blog.heckel.xyz/2013/08/04/use-sslsplit-to-transparently-sniff-tls-ssl-connections/>

[1]: <http://www.roe.ch/SSLsplit>
