#!/usr/bin/env python3

import subprocess
from flask import Flask, render_template_string, redirect, url_for

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>tmux Window Switcher</title>
  <style>
    body { font-family: sans-serif; padding: 20px; }
    .btn { display: block; margin: 8px 0; padding: 10px; background: #ddd; text-decoration: none; color: #000; width: 200px; }
  </style>
</head>
<body>
  <h1>tmux Windows</h1>
  {% for win in windows %}
    <a class="btn" href="{{ url_for('switch_window', target=win['id']) }}">{{ win['id'] }}: {{ win['name'] }}</a>
  {% endfor %}
</body>
</html>
"""

def get_windows():
    out = subprocess.check_output(["tmux", "list-windows", "-F", "#{window_id} #{window_name}"])\
          .decode().strip().splitlines()
    windows = []
    for line in out:
        parts = line.split(" ", 1)
        windows.append({"id": parts[0], "name": parts[1] if len(parts) > 1 else ""})
    return windows

@app.route("/")
def index():
    return render_template_string(HTML, windows=get_windows())

@app.route("/switch/<target>")
def switch_window(target):
    subprocess.call(["tmux", "select-window", "-t", target])
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
