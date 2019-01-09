# picam
A raspberry pi-powered home camera

# Prerequisites
* A DNS name with Google Domains
* A TLS certificate with Let's Encrypt
* A Rapsberry Pi
* A Raspberry Pi camera
* An internet connection
* A `client_secret.json` file from [Google Developer APIs](https://console.developers.google.com/apis/credentials) for OATH 2.0 authentication.
* Create `user.env` with a space-delimited list of allowed e-mail addresses.
* Create `.env` file with values for the environment variables in `docker-compose.yml`.

# Installation
1. Clone the git repo into the desired host.
1. Run `bin/setup` from a shell to install Debian packages and create a virtual environment for Python3.
1. Run `bin/dependencies` from a shell to install python dependcies in your virtual environment.
1. Run `bin/dns` with the desired USERNAME, PASSWORD, SUB_DOMAIN, and DOMAIN in Google Domains to schedule a CRON job that updates DNS with your dynamic IP address.
1. Follow the instructions on [Let's Encrypt](https://letsencrypt.org/getting-started/) to create a TLS certificate.
1. Run `bin/cert` from a shell to schedule a CRON that renews the TLS certificates.
1. Run `bin/copy-cert` to copy the certificates for your domain into the repo root.
    1. Run `bin/generate-cert` to create a self-signed TLS certificate in the repo root.
1. Run `bin/run` to execute the camera.


# Assumptions
The `bin/copy-cert` script assumes that the Raspberry Pi's OS is Hypriot (it uses `chown` for the default hypriot user name).
When exposing your Pi to the Internet, make sure to change the password from the default for the `pirate` user.

# References
* See [pyimagesearch](https://www.pyimagesearch.com/2018/08/15/how-to-install-opencv-4-on-ubuntu/) for instructions on installing OpenCV on Ubuntu.
* See [pyimagesearch](https://www.pyimagesearch.com/2018/09/26/install-opencv-4-on-your-raspberry-pi/) for instructions on installing OpenCV on Raspberry Pi.
* See [sign-in](https://developers.google.com/identity/sign-in/web/sign-in#before_you_begin) for JS auth sample code.
* See [backend-auth](https://developers.google.com/identity/sign-in/web/backend-auth) for python code samples.
* See [balena.io](https://www.balena.io/blog/building-arm-containers-on-any-x86-machine-even-dockerhub/) and [ownyourbits.com](https://ownyourbits.com/2018/06/27/running-and-building-arm-docker-containers-in-x86/) for information on how to run and build an ARM container in an x86 system.
