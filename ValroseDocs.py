from flask import Flask, jsonify
import requests, yaml, os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

if os.environ.get('FLASK_ENV') != 'development':
  import flask_monitoringdashboard as dashboard
  dashboard.bind(app)

config = None

with open("static/config.yml", "r") as stream:
  try:
    config = yaml.safe_load(stream)
  except yaml.YAMLError as exc:
    print(exc)

@app.route('/api/get_data', methods=['GET'])
def api_get_data():

  reqUrl = f"https://www.mathcha.io/api/init2?sharedLink={config['base_folder']['sharedLink']}"
  
  headersList = {
    "Accept": "application/json",
    "Content-Type": "application/json"
  }

  response = requests.request("GET", reqUrl, headers=headersList)
  data = response.json()["sharedTree"]["directories"]
  valrose = [f for f in data if f['id'] == config['base_folder']['id']][0]
  resp_data = valrose["directories"]

  c = config["conversion"]
  ti = config["tag_image"]

  periods = []
  p_i = 0
  for p in resp_data:
    if p["id"] not in c: continue
    periods.append({})
    periods[p_i]["id"] = p["id"]
    if "name" in c[p["id"]]:
      periods[p_i]["name"] = c[p["id"]]["name"]
    if "tag" in c[p["id"]]:
      periods[p_i]["tag"] = c[p["id"]]["tag"]
    if "image" in c[p["id"]]:
      periods[p_i]["image"] = c[p["id"]]["image"]
    units = []
    u_i = 0
    for u in p["directories"]:
      units.append({})
      units[u_i]["id"] = u["id"]
      units[u_i]["name"] = c[u["id"]]["name"] if "name" in c[u["id"]] else u["name"]
      if "tag" in c[u["id"]]:
        units[u_i]["tag"] = c[u["id"]]["tag"]
      units[u_i]["image"] = c[u["id"]]["image"] if "image" in c[u["id"]] else "file.svg"
      lessons = []
      l_i = 0
      for l in u["directories"]:
        if "shared" not in l or l["shared"] != True: continue
        if len(l["documents"]) != 1: continue
        lessons.append({})
        lessons[l_i]["id"] = l["documents"][0]["id"]
        lessons[l_i]["name"] = l["documents"][0]["name"]
        lessons[l_i]["tag"] = l["name"]
        lessons[l_i]["image"] = ti[l["name"]] if l["name"] in ti else "file.svg"
        lessons[l_i]["url"] = l["generatedLink"] + "?embedded=true"
        l_i += 1
      units[u_i]["children"] = lessons
      u_i += 1
    periods[p_i]["children"] = units
    p_i += 1

  response = jsonify(periods)
  return response
