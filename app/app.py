import requests
from pprint import pprint as pp
from datetime import datetime
import os
import glob
import time
from socket import gethostname
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


from dotenv import load_dotenv

load_dotenv()



openweather_api_url = "http://api.openweathermap.org/data/2.5/weather"

openweather_api_key = os.environ["OPEN_WEATHER_API_KEY"]

openweather_api_zip = os.environ["OPEN_WEATHER_ZIP_CODE"]

influxdb_token = os.environ["INFLUXDB_TOKEN"]

influxdb_url = os.environ["INFLUXDB_URL"]

influxdb_org = os.environ["INFLUXDB_ORG"]

influxdb_bucket = os.environ["INFLUXDB_BUCKET"]

def get_weather():
    params = {
        "appid":openweather_api_key,
        "zip":openweather_api_zip,
        "units":"imperial"
    }

    res = requests.post(url=openweather_api_url, params=params)
    return res.json()

def get_ds18b20_temps():
    base_dir = "/sys/bus/w1/devices/"
    readings = []
    if os.path.exists(base_dir):
        device_folders = glob.glob(base_dir + "28*")
        for device_folder in device_folders:
            device_file = device_folder + "/w1_slave"
            temp = read_ds18b20(device_file)
            if temp:
                readings.append(read_ds18b20(device_file))
    else:
        raise FileNotFoundError("Temperature Probes not Active!")

    return readings


def read_ds18b20_raw(device_file):
    with open(device_file, "f") as f:
        lines = f.readlines()

    return lines

def read_ds18b20(device_file):
    device_addr = os.path.basename(os.path.dirname(device_file))
    lines = read_ds18b20_raw(device_file)
    while lines[0].strip()[-3:] != "YES":
        time.sleep(0.2)
        lines = read_ds18b20_raw(device_file)
    equals_pos = lines[1].find("t=")
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0

        return {
            device_addr: {
                "temp_c":temp_c,
                "temp_f":temp_f
            }
        }

    return None



def write_data_to_influx():


    client = InfluxDBClient(url=influxdb_url, token=influxdb_token)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    weather = get_weather()

    point = Point("weather")\
        .tag("host", gethostname())\
        .field("temperature", weather["main"]["temp"])\
        .field("humidity", weather["main"]["humidity"])\
        .field("feels_like", weather["main"]["feels_like"])\
        .field("pressure", weather["main"]["pressure"])\
        .field("weather_dsc", weather["weather"][0]["description"])\
        .field("weather_id", weather["weather"][0]["id"])

    write_api.write(influxdb_bucket, influxdb_org, point)

    for reading in get_ds18b20_temps():
        for key, value in reading.items():
            point = Point("temp_probe")\
                .tag("host", gethostname())\
                .tag("probe_addr", key)\
                .field("temp_c", value["temp_c"])\
                .field("temp_f", value["temp_f"])

            write_api.write(influxdb_bucket, influxdb_org, point)



while True:
    try:
        write_data_to_influx()
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(e)

    time.sleep(30)