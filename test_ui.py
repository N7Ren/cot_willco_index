import urllib.request
import time
import subprocess

# Start flask app
proc = subprocess.Popen(["python", "index.py"])
time.sleep(3) # Wait for it to start
try:
    req = urllib.request.urlopen('http://127.0.0.1:5000')
    html = req.read().decode('utf-8')
    print("HTML length:", len(html))
    print("Title count:", html.count("<title>"))
finally:
    proc.terminate()
