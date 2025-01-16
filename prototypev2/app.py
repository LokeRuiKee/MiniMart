from flask import Flask, Response, send_from_directory, jsonify
from flask_cors import CORS
from main import generate_video_feed
import config
import pyodbc

app = Flask(__name__)
CORS(app)

@app.route('/video_feed')
def video_feed():
    return Response(generate_video_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_json')
def get_json():
    return send_from_directory(config.JSON_DIRECTORY, config.JSON_FILE_NAME)

# Database configuration
DB_CONFIG = {
    'server': 'PTPNTE818',
    'database': 'miniMart',
    'driver': '{SQL Server}',
    'trusted_connection': 'yes'
}

@app.route('/item_details', methods=['GET'])
def get_item_details():
    try:
        # Create database connection
        conn = pyodbc.connect(
            f"DRIVER={DB_CONFIG['driver']};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"Trusted_Connection={DB_CONFIG['trusted_connection']};"
        )
        cursor = conn.cursor()

        # Query the database
        cursor.execute("SELECT * FROM [miniMart].[dbo].[item_list]")
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # Return results as JSON
        return jsonify(results)

    except Exception as e:
        print("Error executing query:", str(e))
        return jsonify({"error": str(e)}), 500

    finally:
        # Close the connection
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    app.run()
