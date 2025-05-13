from flask import Flask, jsonify, request
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
DATABASE_URL = os.getenv('DATABASE_URL')

def get_db():
    return psycopg2.connect(DATABASE_URL)

@app.get('/convert')
def convert():
    currency = request.args.get('currency')
    amount = float(request.args.get('amount'))
    
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT rate FROM currencies WHERE currency_name = %s", (currency,))
        rate = cur.fetchone()
        if not rate:
            return jsonify({"error": "Currency not found"}), 404
            
        result = amount * float(rate[0])
        return jsonify({"result": round(result, 2)}), 200
    finally:
        cur.close()
        conn.close()

@app.get('/currencies')
def get_currencies():
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT currency_name, rate FROM currencies")
        currencies = [{"name": row[0], "rate": row[1]} for row in cur.fetchall()]
        return jsonify(currencies), 200
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    app.run(port=5002)