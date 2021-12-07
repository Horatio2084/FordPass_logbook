import datetime
from influxdb import InfluxDBClient
from fordpass import Vehicle

# Connection to Ford API  FordPASS
v = Vehicle("your@FordPass.mail", "FP_Password", "FIN of Vehicle")

# Connection to InfluxDB
client = InfluxDBClient('Hostname/IP Influx', 'Port Influx', 'User', 'Password', 'Databasename')



# Get Data from Ford API
v_data = v.status()

# Get Last Entry from Influx
last_entry = client.query("select* from Location ORDER BY time DESC LIMIT 1;")
new_data = False
first_data= False
#Check if Last Entry
if last_entry.items():
    # Extract last timestamp from Influx and Convert String to Datetime Object
    last_timestamp_str = list(last_entry.get_points())[0]["timestamp"]
    last_timestamp = datetime.datetime.strptime(last_timestamp_str, "%m-%d-%Y %H:%M:%S")

    # Extract timestamp form API Data and Convert it to Datetime Object
    timestamp_act_str = v_data["gps"]["timestamp"]
    timestamp_act = datetime.datetime.strptime(timestamp_act_str, "%m-%d-%Y %H:%M:%S")

    if timestamp_act > last_timestamp:
        new_data = True

else:
    first_data = True

# Check if Data to Write AND Ignition is Off
if (first_data or new_data) and v_data["ignitionStatus"]["value"] == "Off":
    data = []
    data.append(
        {
            "measurement": "Location",

            "fields": {
                "latitude": float(v_data["gps"]["latitude"]),
                "longitude": float(v_data["gps"]["longitude"]),
                "odometer": int(v_data["odometer"]["value"]),
                "timestamp": str(v_data["gps"]["timestamp"]),

            },
        }
    )
    client.write_points(data)

