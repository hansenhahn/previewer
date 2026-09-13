import os

from flask import Blueprint, current_app, jsonify, render_template, send_from_directory

bp = Blueprint("main", __name__)


@bp.get("/")
def index():
    dist = os.path.join(current_app.root_path, "static", "dist")
    if os.path.isfile(os.path.join(dist, "index.html")):
        response = send_from_directory(dist, "index.html")
        response.headers["Cache-Control"] = "no-store"
        return response
    return render_template("index.html")


@bp.get("/healthz")
def healthz():
    database = current_app.extensions["database"]
    if database.is_healthy():
        return jsonify(status="ok"), 200
    return jsonify(status="degraded"), 503
