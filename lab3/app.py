from flask import Flask, request, jsonify
import random

app = Flask(__name__)
operations = ['sum', 'sub', 'mul', 'div']

# GET эндпоинт с параметром запроса
@app.route('/number/', methods=['GET'])
def get_number():
    # Получаем параметр из query string
    param = request.args.get('param')
    
    # Валидация параметра
    if not param:
        return jsonify({"error": "Missing 'param' parameter"}), 400
    try:
        num = int(param)
    except ValueError:
        return jsonify({"error": "Parameter must be a number"}), 400

    # Генерация результата
    random_num = random.randint(1, 100)
    result = random_num * num
    
    return jsonify({
        "number": result,
        "operation": random.choice(operations)
    })

# POST эндпоинт с телом JSON
@app.route('/number/', methods=['POST'])
def post_number():
    # Проверка формата запроса
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    
    # Валидация параметра
    if 'jsonParam' not in data:
        return jsonify({"error": "Missing 'jsonParam' in JSON"}), 400
    
    try:
        num = int(data['jsonParam'])
    except (ValueError, TypeError):
        return jsonify({"error": "jsonParam must be a number"}), 400

    # Генерация результата
    random_num = random.randint(1, 100)
    result = random_num * num
    
    return jsonify({
        "number": result,
        "operation": random.choice(operations)
    })

# DELETE эндпоинт
@app.route('/number/', methods=['DELETE'])
def delete_number():
    # Генерация случайного числа
    random_num = random.randint(1, 100)
    
    return jsonify({
        "number": random_num,
        "operation": random.choice(operations)
    })

if __name__ == '__main__':
    app.run(debug=True)