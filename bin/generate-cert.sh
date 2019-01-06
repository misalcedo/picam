#!/usr/bin/env bash

openssl req -newkey rsa:2048 -nodes -keyout privkey.pem -x509 -days 365 -out fullchain.pem
head -1 /dev/random -c32 > symmetric.key && chmod 600 symmetric.key
