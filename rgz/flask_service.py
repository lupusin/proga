from flask import Flask, request, jsonify

app = Flask(__name__)

# Статические курсы валют
STATIC_RATES = {
    "USD": 90.5,
    "EUR": 97.2
}

@app.route("/rate",methods=['GET'])
def get_rate():
    try:
        currency = request.args.get("currency")

        if currency not in STATIC_RATES:
            return jsonify({"message": "UNKNOWN CURRENCY"}), 400

        return jsonify({"rate": STATIC_RATES[currency]}), 200

    except Exception as e:
        return jsonify({"message": "UNEXPECTED ERROR"}), 500

if __name__ == "__main__":
    app.run(debug=True)
