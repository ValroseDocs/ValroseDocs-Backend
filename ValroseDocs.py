from flask import Flask, render_template, request, jsonify
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

@app.route('/')
def index():
  step1=request.args.get('step1')
  step2=request.args.get('step2')
  step3=request.args.get('step3')
  data = get_data()
  c = config["conversion"]
  ti = config["tag_image"]
  
  if step1 != None:
    dir = [d for d in data if d['id'] == step1]
    if len(dir) == 0: return not_found()
    if "directories" not in dir[0]:
      return not_found()
    data = dir[0]["directories"]
  
  if step2 != None:
    dir = [d for d in data if d['id'] == step2]
    if len(dir) == 0: return not_found()
    if "directories" not in dir[0]:
      return not_found()
    data = dir[0]["directories"]
  
  parsed_data = []
  for i, s in enumerate(data):
    if step2 != None:
      if len(s["documents"]) != 1: continue
      if "generatedLink" not in s or s["generatedLink"] == None: continue
    parsed_data.append({})
    if s["id"] in c and "name" in c[s["id"]]:
      parsed_data[i]["name"] = c[s["id"]]["name"]
    else:
      if step2 != None:
        parsed_data[i]["name"] = s["documents"][0]["name"]  
      else:
        parsed_data[i]["name"] = s["name"]
    if s["id"] in c and "image" in c[s["id"]]:
      parsed_data[i]["image"] = c[s["id"]]["image"]
    else:
      if step2 != None and s["name"] in ti:
        parsed_data[i]["image"] = ti[s["name"]]
      else:
        parsed_data[i]["image"] = "file.svg"
    if s["id"] in c and "tag" in c[s["id"]]:
      parsed_data[i]["tag"] = c[s["id"]]["tag"]
    elif step2 != None and s["name"] != "":
      parsed_data[i]["tag"] = s["name"]
    if step1 == None:
      parsed_data[i]["url"] = f"/?step1={s['id']}"
    elif step2 == None:
      parsed_data[i]["url"] = f"/?step1={step1}&step2={s['id']}"
    else:
      parsed_data[i]["url"] = f"{s['generatedLink']}?embedded=true"
  
  step1btn = f'/' if step1 is not None else '#'
  step2btn = f'/?step1={step1}' if step2 is not None else '#'
  
  
  return render_template(
    'index.html',
    step1=step1,
    step2=step2,
    step3=step3,
    step1btn=step1btn,
    step2btn=step2btn,
    data=parsed_data,
    data_len=len(parsed_data)
  )

def not_found():
  return render_template('notfound.html')

@app.errorhandler(404)
def page_not_found(e):
  return not_found()

def get_data():
  reqUrl = f"https://www.mathcha.io/api/init2?sharedLink={config['base_folder']['sharedLink']}"
  headersList = {
    "Accept": "application/json",
    "Content-Type": "application/json"
  }

  response = requests.request("GET", reqUrl, headers=headersList)
  data = response.json()["sharedTree"]["directories"]
  valrose = [f for f in data if f['id'] == config['base_folder']['id']][0]
  return valrose["directories"]

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
        lessons[l_i]["url"] = l["generatedLink"]
        l_i += 1
      units[u_i]["children"] = lessons
      u_i += 1
    periods[p_i]["children"] = units
    p_i += 1

  response = jsonify(periods)
  return response
