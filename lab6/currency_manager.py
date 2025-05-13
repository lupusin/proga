from flask import Flask, request, jsonify
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
DATABASE_URL = os.getenv('DATABASE_URL')

def get_db():
    return psycopg2.connect(DATABASE_URL)

@app.post('/load')
def load_currency():
    data = request.json
    currency_name = data.get('currency_name')
    rate = data.get('rate')
    
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM currencies WHERE currency_name = %s", (currency_name,))
        if cur.fetchone():
            return jsonify({"error": "Currency exists"}), 400
            
        cur.execute(
            "INSERT INTO currencies (currency_name, rate) VALUES (%s, %s)",
            (currency_name, rate)
        )
        conn.commit()
        return jsonify({"message": "Currency added"}), 200
    finally:
        cur.close()
        conn.close()

@app.post('/update_currency')
def update_currency():
    data = request.json
    currency_name = data.get('currency_name')
    new_rate = data.get('rate')
    
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM currencies WHERE currency_name = %s", (currency_name,))
        if not cur.fetchone():
            return jsonify({"error": "Currency not found"}), 404
            
        cur.execute(
            "UPDATE currencies SET rate = %s WHERE currency_name = %s",
            (float(new_rate), currency_name)
        )
        conn.commit()
        return jsonify({"message": "Currency updated"}), 200
    finally:
        cur.close()
        conn.close()

@app.post('/delete')
def delete_currency():
    currency_name = request.json.get('currency_name')
    
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM currencies WHERE currency_name = %s", (currency_name,))
        if not cur.fetchone():
            return jsonify({"error": "Currency not found"}), 404
            
        cur.execute("DELETE FROM currencies WHERE currency_name = %s", (currency_name,))
        conn.commit()
        return jsonify({"message": "Currency deleted"}), 200
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    app.run(port=5001)