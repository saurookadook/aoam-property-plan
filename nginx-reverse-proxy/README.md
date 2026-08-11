# NGINX Reverse Proxy

## Setup

Install and set up `mkcert`

```sh
brew install mkcert
mkcert -install
```

Then restart any web browsers you have open.

## Generate Local Certificates

From the root of this repo, run:

```sh
chmod +x ./nginx-reverse-proxy/local_insall.sh
./nginx-reverse-proxy/local_insall.sh
```
