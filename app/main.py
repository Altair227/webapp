from flask import Flask
import multiprocessing


app = Flask(__name__)

app.config["GUNICORN_OPTIONS"] = {
    "workers": multiprocessing.cpu_count() * 2 + 1,
    "worker_class": "sync",
    "timeout": 30,
    "accesslog": "-",
    "errorlog": "-",
    "loglevel": "info",
    "reload": True,
}


@app.route("/")
def index():
    return "<h1> hello world </h1>"
