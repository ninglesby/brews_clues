# Brews Clues

## What's this about

My partner and I were taking our first foray into home brewing. She was doing most of the work, but it was annoying to keep checking the temperature in our un-air-conditioned apartment and swap in and out ice. So of course I whipped up an over-complicated temperature monitoring solution.

## Parts

### Hardware

- Raspberry Pi 3
- [ds18b20](https://www.amazon.com/gp/product/B087JQ6MCP/ref=ppx_yo_dt_b_asin_title_o00_s00?ie=UTF8&psc=1) - temperature sensor monitor

### Software

- Ubuntu 20 Server arm64 for the raspberry pi
- Grafana
- InfluxDB
- docker
- docker-compose

## Process

### get open weather account

I was curious to see how much the outside temperature would affect the ambient room temperature and since it wasn't too much more effort I added some other values as well. This is not required, if the `OPEN_WEATHER_API_KEY` is omitted this step is just skipped.

- I am using the [OpenWeather api](https://openweathermap.org/api) to pull in weather data
- You can setup an a free account and get a million calls per month which is plenty for this project.
- Once you have an account you can get an API key, you'll need that later.

### setup raspberry pi

- Download [Ubuntu Server 20](https://cdimage.ubuntu.com/releases/20.04.2/release/ubuntu-20.04.2-preinstalled-server-arm64+raspi.img.xz)
- Use something like [balenaEtcher](https://github.com/balena-io/etcher/releases) to get the image on an SD card
- Go through the install process
- get updates `sudo apt-get update`
- run upgrades `sudo apt-get upgrade`
- install software
  - `sudo apt-get install docker.io`
  - `sudo apt-get install docker-compose`
- setup the pi for the the sensors
  - `sudo nano /boot/firmware/user-cfg.txt`
  - add the line `dtoverlay=w1-gpio`
  - reboot
  - enter the command `sudo modprobe w1-therm`
  - `sudo modprobe w1-gpio`
- clone the project, for the systemd script to work you should clone it into `/opt` folder:
  - `cd /opt`
  - `git clone https://github.com/ninglesby/brews_clues.git`
- set up the systemd script so it can start on reboot
  - `cd brews_clues`
  - `sudo cp docker-compose@brews_clues.service /etc/systemd/system/docker-compose@brews_clues.service`
  - `sudo systemctl enable docker-compose@brews_clues.service`
  - `sudo systemctl daemon-reload`
- setup environment variables
  - there is an example `.env` file in the directory
  - `sudo mv example.env .env`
  - for the `OPEN_WEATHER_API_KEY` grab the key you made earlier
  - for the rest of entries you can entire whatever you'd like, try to make the passwords secure and all that.
  - the only thing that needs to stay the same as the example file is the `INFLUXDB_URL`

That should be it, start the process with `sudo systemctl start docker-compose@brews_clues.service`
![image](https://user-images.githubusercontent.com/29129252/129919189-0d3bd94d-b423-4873-95e8-385d1205cc20.png)

*This guide is a work in progress, I am just writing this down from memory I haven't gone through it yet to make sure everything works as written.
