from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx,uvicorn,requests
from pydantic import BaseModel
from backend.nearest_station import haversine
from backend.ups_state import parse_upsc_output,get_light_color

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
    )

class PowerStatus(BaseModel):
    reserve_percent: float
    reserve_w: float
    indicator: str

class Location(BaseModel):
    lon:float
    lat:float

class UPSStatus(BaseModel):
    battery_charge: int
    battery_runtime: int
    ups_status: str
    ups_load: int
    input_voltage: int
    output_voltage: int
    light: str


#taipower power supply open data api
@app.get("/api/power_supply", response_model=PowerStatus)
async def get_power_status():
    url = r"https://service.taipower.com.tw/data/opendata/apply/file/d006020/001.json"
    try:
        async with httpx.AsyncClient(timeout=10.0,proxy="http://Tommy.Huang:sasWAfer%21@@ProxySG.saswafer.com:8080") as client:
            res = await client.get(url)
            data = res.json()
        curr_load = float(data["records"][0]["curr_load"])
        sply_capacity = float(data["records"][3]["real_hr_maxi_sply_capacity"])
        reserve_w = sply_capacity - curr_load
        reserve_percent = (reserve_w / curr_load) * 100

        #determine indicator and rules with color change behined 
        if reserve_w < 50:
            indicator = "black"
        elif reserve_w < 90:
            indicator = "red"
        elif reserve_percent < 6:
            indicator = "orange"
        elif reserve_percent < 10:
            indicator = "yellow"
        else:
            indicator = "green"
        return PowerStatus(reserve_percent=round(reserve_percent,2),reserve_w=round(reserve_w,1),indicator=indicator)

    except httpx.ConnectTimeout:
        raise HTTPException(status_code=504, detail="Connect Timeout")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"HTTP Error:{str(e)}")


@app.post("/api/gps_location")
async def receive_location(location: Location):
    return {"status": "Location Received", "lat": location.lat, "lon": location.lon}


@app.post("/api/weather")
async def get_nearest_station(location: Location):
    lat, lon = location.lat, location.lon
    url = r"https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001?Authorization=CWA-88D62B68-5C16-456B-8D80-E11CAD258497"
    try:
        async with httpx.AsyncClient(timeout=10.0,proxy="http://Tommy.Huang:sasWAfer%21@@ProxySG.saswafer.com:8080",verify=False) as client:
            res = await client.get(url)
            data = res.json()

        stations = data['records']['Station']

        def get_wgs84_coords(st):
            for coord in st['GeoInfo']['Coordinates']:
                if coord['CoordinateName'] == 'WGS84':
                    return float(coord['StationLongitude']), float(coord['StationLatitude'])
            return None, None

        nearest = min(stations,key=lambda st: haversine(lon, lat,*get_wgs84_coords(st)))
        nearest_lon, nearest_lat = get_wgs84_coords(nearest)
        distance = haversine(lon, lat, nearest_lon, nearest_lat)

        return {
            "stationId": nearest["StationId"],"stationName": nearest["StationName"],"CountyName":nearest["GeoInfo"]["CountyName"],
            "lat": nearest_lat,"lon": nearest_lon,
            "distance_km": round(distance,2),"weather": nearest["WeatherElement"],
        }

    except Exception as e:
        return {"Error": f"Unable to connect to CWB API: {str(e)}"}

@app.get("/api/ups")
def get_ups_status():
    ups_data = parse_upsc_output()
    battery_charge = int(ups_data.get("battery.charge", "0"))
    battery_runtime = int(ups_data.get("battery.runtime", "0"))
    ups_status = ups_data.get("ups.status", "UNKNOWN")
    ups_load = int(ups_data.get("ups.load", "0"))
    input_voltage = int(ups_data.get("input.voltage", "0"))
    output_voltage = int(ups_data.get("output.voltage", "0"))

    light = get_light_color(ups_status, battery_charge)

    return UPSStatus(
        battery_charge=battery_charge,
        battery_runtime=battery_runtime,
        ups_status=ups_status,
        ups_load=ups_load,
        input_voltage=input_voltage,
        output_voltage=output_voltage,
        light=light
    )



if __name__=="__main__":
    uvicorn.run("main:app",reload=True)