from flask import Flask, request, jsonify
import requests, json
from math import radians, cos, sin, asin, sqrt

app = Flask(__name__)
API_KEY = "CWA-A8587709-50A6-4D65-B6A0-4A9A4D0BC2DC"

# 讀取測站清單
with open("stations.json", "r", encoding="utf-8") as f:
    stations = json.load(f)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # 地球半徑，單位為公里
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

@app.route("/weather", methods=["GET"])
def get_weather():
    user_ip = request.remote_addr

    # 使用 ipwho.is 取得使用者的經緯度
    try:
        geo_resp = requests.get(f"https://ipwho.is/{user_ip}").json()
        if not geo_resp.get("success"):
            return jsonify({"error": "IP geolocation failed"}), 500
        lat = float(geo_resp["latitude"])
        lon = float(geo_resp["longitude"])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # 找出距離使用者最近的測站
    closest_station = min(stations, key=lambda s: haversine(lat, lon, s["lat"], s["lon"]))
    station_id = closest_station["id"]

    # 取得中央氣象局測站資料
    try:
        url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0001-001?Authorization={API_KEY}&stationId={station_id}"
        resp = requests.get(url).json()
        record = resp["records"]["location"][0]
        weather = {
            "station": record["locationName"],
            "temperature": float(record["weatherElement"][3]["elementValue"]),
            "humidity": float(record["weatherElement"][4]["elementValue"]),
            "windSpeed": float(record["weatherElement"][2]["elementValue"]),
            "weather": record["weatherElement"][20]["elementValue"]
        }
        return jsonify(weather)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
