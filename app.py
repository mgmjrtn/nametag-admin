"""
Nametag Demo Admin — Configuration Manager
Lightweight Flask app for managing Google Sheets config.
No Google Cloud account needed — uses public CSV export for reads
and a free Apps Script web app for writes.
"""

import os
import csv
import io
import requests
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "nametag-admin-dev-key")

# ---------------------------------------------------------------------------
# Config — all from env vars, with defaults matching your sheets
# ---------------------------------------------------------------------------
DATA_SHEET_ID = os.environ.get(
    "DATA_SHEET_ID", "1u1R73O85R3IzDZM8isenlCgl7VoSk1KGXSK-v7sP-1s"
)
TIMECARD_SHEET_ID = os.environ.get(
    "TIMECARD_SHEET_ID", "1scOTX6sEwCW3UvudERIMoZUtzCmxkDkZoFBaQacdfH0"
)
# Apps Script Web App URL — deployed once for free (see README)
APPS_SCRIPT_URL = os.environ.get("APPS_SCRIPT_URL", "")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def read_sheet(sheet_id, gid="0"):
    """Read a public Google Sheet via CSV export. Returns list of rows."""
    url = (
        f"https://docs.google.com/spreadsheets/d/{sheet_id}"
        f"/export?format=csv&gid={gid}"
    )
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    reader = csv.reader(io.StringIO(resp.text))
    return list(reader)


def write_sheet(sheet_id, action, **kwargs):
    """POST a write command to the Apps Script proxy."""
    if not APPS_SCRIPT_URL:
        raise RuntimeError(
            "APPS_SCRIPT_URL is not set. Deploy the Apps Script first (see README)."
        )
    payload = {"sheetId": sheet_id, "action": action, **kwargs}
    resp = requests.post(APPS_SCRIPT_URL, json=payload, timeout=20)
    resp.raise_for_status()
    return resp.json()


# ===== LANDING PAGE ==========================================================

@app.route("/")
def index():
    return render_template("index.html")


# ===== DOCS PAGE ===============================================================

@app.route("/docs")
def docs():
    return render_template("docs.html")


# ===== DATA CONFIG — full CRUD on rows 2+ ====================================

@app.route("/data-config")
def data_config():
    try:
        rows = read_sheet(DATA_SHEET_ID)
    except Exception as e:
        flash(f"Could not read sheet: {e}", "error")
        rows = []
    entries = []
    for i, row in enumerate(rows[1:], start=2):
        entries.append({
            "row": i,
            "name": row[0] if len(row) > 0 else "",
            "link": row[1] if len(row) > 1 else "",
        })
    return render_template("data_config.html", entries=entries)


@app.route("/data-config/add", methods=["POST"])
def data_config_add():
    name = request.form.get("name", "").strip()
    link = request.form.get("link", "").strip()
    if not name:
        flash("Source Name is required.", "error")
        return redirect(url_for("data_config"))
    try:
        write_sheet(DATA_SHEET_ID, "append", values=[name, link])
        flash(f"Added '{name}'.", "success")
    except Exception as e:
        flash(f"Write failed: {e}", "error")
    return redirect(url_for("data_config"))


@app.route("/data-config/update/<int:row>", methods=["POST"])
def data_config_update(row):
    name = request.form.get("name", "").strip()
    link = request.form.get("link", "").strip()
    try:
        write_sheet(DATA_SHEET_ID, "update", row=row, values=[name, link])
        flash(f"Row {row} updated.", "success")
    except Exception as e:
        flash(f"Write failed: {e}", "error")
    return redirect(url_for("data_config"))


@app.route("/data-config/delete/<int:row>", methods=["POST"])
def data_config_delete(row):
    try:
        write_sheet(DATA_SHEET_ID, "delete", row=row)
        flash("Row deleted.", "success")
    except Exception as e:
        flash(f"Write failed: {e}", "error")
    return redirect(url_for("data_config"))


# ===== TIMECARD CONFIG — full CRUD on rows 2+ ================================

@app.route("/timecard-config")
def timecard_config():
    try:
        rows = read_sheet(TIMECARD_SHEET_ID)
    except Exception as e:
        flash(f"Could not read sheet: {e}", "error")
        rows = []
    entries = []
    for i, row in enumerate(rows[1:], start=2):
        entries.append({
            "row": i,
            "field": row[0] if len(row) > 0 else "",
            "description": row[1] if len(row) > 1 else "",
        })
    return render_template("timecard_config.html", entries=entries)


@app.route("/timecard-config/add", methods=["POST"])
def timecard_config_add():
    field = request.form.get("field", "").strip()
    description = request.form.get("description", "").strip()
    if not field:
        flash("Field name is required.", "error")
        return redirect(url_for("timecard_config"))
    try:
        write_sheet(TIMECARD_SHEET_ID, "append", values=[field, description])
        flash(f"Added '{field}'.", "success")
    except Exception as e:
        flash(f"Write failed: {e}", "error")
    return redirect(url_for("timecard_config"))


@app.route("/timecard-config/update/<int:row>", methods=["POST"])
def timecard_config_update(row):
    field = request.form.get("field", "").strip()
    description = request.form.get("description", "").strip()
    try:
        write_sheet(TIMECARD_SHEET_ID, "update", row=row, values=[field, description])
        flash(f"Row {row} updated.", "success")
    except Exception as e:
        flash(f"Write failed: {e}", "error")
    return redirect(url_for("timecard_config"))


@app.route("/timecard-config/delete/<int:row>", methods=["POST"])
def timecard_config_delete(row):
    try:
        write_sheet(TIMECARD_SHEET_ID, "delete", row=row)
        flash("Row deleted.", "success")
    except Exception as e:
        flash(f"Write failed: {e}", "error")
    return redirect(url_for("timecard_config"))


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
