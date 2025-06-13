from flask import Flask, render_template, request, send_file
import pandas as pd
import mysql.connector
from datetime import datetime
import os



app = Flask(__name__)
DB_CONFIG = {
    "host": "localhost",
    "user": "rachel",
    "password": "Stage.2025",
    "database": "Stage"
}

def fetch_data(table, start_date=None, end_date=None):
    conn = mysql.connector.connect(**DB_CONFIG)
    query = f"SELECT * FROM {table}"
    if start_date and end_date:
        query += f" WHERE timestamp BETWEEN '{start_date}' AND '{end_date}'"
    query += " ORDER BY timestamp DESC"  # <- tri du plus récent au plus ancien
    df = pd.read_sql(query, conn)
    conn.close()
    return df


@app.route('/', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def dashboard():
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")

    tables = ["luminosite", "presence", "intensite"]
    dataframes = {}
    merged_data = pd.DataFrame()

    for table in tables:
        df = fetch_data(table, start_date, end_date)
        dataframes[table] = {
            "html": df.to_html(classes='table table-bordered table-sm', index=False),
            "json": df.to_dict(orient='records')
        }
        if merged_data.empty:
            merged_data = df
        else:
            merged_data = pd.merge(merged_data, df, on="timestamp", how="outer")

    merged_data = merged_data.sort_values("timestamp")
    merged_json = merged_data.to_dict(orient="records")

    return render_template("dashboard.html",
                           dataframes=dataframes,
                           merged_json=merged_json,
                           start_date=start_date,
                           end_date=end_date)


@app.route('/download', methods=['POST'])
def download_excel():
    table = request.form.get("table")
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")
    df = fetch_data(table, start_date, end_date)

    filename = f"{table}_report.csv"
    path = os.path.join("static", filename)
    df.to_csv(path, index=False)

    return send_file(path, as_attachment=True, mimetype='text/csv', download_name=filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5011)
