#!/usr/bin/env python3

#TODO: Add new window feature

import subprocess
from flask import Flask, render_template, redirect, url_for, jsonify

app = Flask(__name__,static_url_path='/static', static_folder='static', template_folder='templates')

def get_windows():
    out = subprocess.check_output(["tmux", "list-windows", "-F", "#{window_index} #{window_name}"])\
          .decode().strip().splitlines()
    windows = []
    for line in out:
        parts = line.split(" ", 1)
        windows.append({"id": parts[0], "name": parts[1] if len(parts) > 1 else ""})
    return windows

@app.route("/")
def index():
    return render_template("index.html", windows=get_windows())

@app.route("/windows")
def windows():
    return jsonify(get_windows())

@app.route("/switch/<target>")
def switch_window(target):
    subprocess.call(["tmux", "select-window", "-t", target])
    return redirect(url_for('index'))

@app.route("/close/<target>", methods=["POST"])
def close_window(target):
    subprocess.call(["tmux", "kill-window", "-t", target])
    return ('', 204)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
