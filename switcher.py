#!/usr/bin/env python3

import subprocess
from flask import Flask, render_template_string, redirect, url_for, jsonify

app = Flask(__name__)

#TODO: separate template and styles
#TODO: move template and styles to separate files

HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>tmux Window Switcher</title>
  <style>
    body { font-family: sans-serif; padding: 20px; display: flex; justify-content: center; }
    .btn { display: block; margin: 4px 0; padding: 6px 12px; background: #ddd; text-decoration: none; color: #000; border-radius: 6px; min-width: 150px; text-align: center; }
  </style>
</head>
<body><div style="width: 320px;">
  <h1>tmux Windows</h1>
  <div id="wins"></div>
<script>
async function refresh() {
  const resp = await fetch('/windows');
  const data = await resp.json();
  const container = document.getElementById('wins');
  container.innerHTML = '';
  data.forEach(win => {
    const wrap = document.createElement('div');
    wrap.style.display = 'flex';
    wrap.style.alignItems = 'center';
    wrap.style.marginBottom = '6px';

    const a = document.createElement('a');
    a.className = 'btn';
    a.href = `/switch/${win.id}`;
    a.textContent = `${win.id}: ${win.name}`;
    a.style.flex = '1';

    const close = document.createElement('button');
    close.textContent = '✕';
    close.title = 'Close window';
    close.style.background = 'red';
    close.style.color = 'white';
    close.style.border = 'none';
    close.style.padding = '6px 10px';
    close.style.marginLeft = '8px';
    close.style.cursor = 'pointer';
    close.onclick = async (e) => {
      e.preventDefault();
      e.stopPropagation();
      if (!confirm('Kill tmux window ' + win.id + '?')) return;
      await fetch(`/close/${win.id}`, { method: 'POST' });
      refresh();
    };

    wrap.appendChild(a);
    wrap.appendChild(close);
    container.appendChild(wrap);
  });
}

// initial load
refresh();
setInterval(refresh, 3000);
</script>
</div></body>
</html>
"""

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
    return render_template_string(HTML, windows=get_windows())

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
