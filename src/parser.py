import json
import requests
import re
import os

VERSION_REGEX = "[0-9][0-9.]*[0-9]"


# get the input and convert it to int
DRY_RUN = os.environ.get("DRY_RUN")
if DRY_RUN:
    try:
        DRY_RUN = bool(str(DRY_RUN).lower() in ("yes", "true", "t", "1"))
    except Exception:
        exit('ERROR: the DRY_RUN provided ("{}") is not an boolean'.format(DRY_RUN))
else:
    DRY_RUN = False


def get_local_manifest_path():
    base_path = "client"
    if os.environ.get("PROJECT_PATH"):
        base_path = str(os.environ.get("PROJECT_PATH"))
    
    return os.path.join(base_path, "Packages", "manifest.json")


def get_latest_version():
    response = requests.get('https://nexus.beamable.com/nexus/content/repositories/unity/com.beamable')
    packages = response.json()
    latest_version = packages["dist-tags"]["latest"]
    if not re.match(VERSION_REGEX, latest_version):
        raise Exception("Latest version is not valid: " + latest_version)
    return latest_version

def get_local_version():
    path = get_local_manifest_path()
    f = open(path, "r")
    x = f.read()
    y = json.loads(x)
    local_version = y["dependencies"]["com.beamable"]
    if not re.match(VERSION_REGEX, local_version):
        raise Exception("Local version is not valid: " + latest_version)
    return local_version

def replace_local_version(new_version):
    path = get_local_manifest_path()
    data = str("")
    with open(path, "r") as f:
        data = f.read()
    dataJson = json.loads(data)
    dataJson["dependencies"]["com.beamable"] = new_version
    if not dataJson["dependencies"].get("com.beamable.server") == None:
        dataJson["dependencies"]["com.beamable.server"] = new_version
    with open(path, "w") as f:
        f.write(json.dumps(dataJson, indent=2))


local_version = get_local_version()
latest_version = get_latest_version()
perform_update = DRY_RUN == False and local_version != latest_version
if perform_update:
    replace_local_version(latest_version)

print("Local: " + local_version)
print("Remote: " + latest_version)
print("Is dry run: " + str(DRY_RUN))
print("Perform update: " + str(perform_update))

# set output
print(f"::set-output name=local_version::{local_version}")
print(f"::set-output name=remote_version::{latest_version}")
print(f"::set-output name=did_perform_update::{str(perform_update)}")
