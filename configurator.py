#!/usr/bin/env python
# encoding: utf-8
import json, os
from flask import Flask, request, render_template

app = Flask(__name__)

TARGETS_FILE_PATH = "targets/targets.json"

def prometheus_target(slm_id, url):
    return {
        "labels": {
            "slm_id": slm_id
        },
        "targets": [
            url
        ]
    }

def read_targets_file() -> list:
    with open(TARGETS_FILE_PATH, encoding="utf8") as f:
        return json.load(f)

def write_targets_file(targets:list):
    with open(TARGETS_FILE_PATH, encoding="utf8", mode="w") as f:
        json.dump(targets, f)

def get_slm_targets(exclude=None):
    slm_targets = {}
    for target in get_targets():
        if exclude != target["labels"]["slm_id"]:
            slm_targets[target["labels"]["slm_id"]] = target["targets"][0]
    return slm_targets

def save_slm_targets(slm_targets):
    targets = []
    for slm_id, url in slm_targets.items():
        targets.append(prometheus_target(slm_id, url))
    write_targets_file(targets)

@app.route('/prometheus/targets', methods=["GET"])
def get_targets():
    return read_targets_file()

@app.route("/prometheus/slm-resource-target", methods=["POST"])
def add_slm_resource_target():
    slm_targets = get_slm_targets()
    slm_targets[request.form["slm_id"]] = request.form["url"]
    save_slm_targets(slm_targets)
    return ""
    
@app.route("/")
def index():
    return render_template("slm_resource_target.html", targets=read_targets_file())

@app.route("/prometheus/slm-resource-target/<slm_id>", methods=["DELETE"])
def delete_slm_resource_target(slm_id):
    slm_targets = get_slm_targets(exclude=slm_id)
    save_slm_targets(slm_targets)
    return ""

if not os.path.exists(TARGETS_FILE_PATH):
    write_targets_file([])

if __name__ == "__main__":
    app.run(host='0.0.0.0')
