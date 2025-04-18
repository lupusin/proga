import requests
import random

# Функция для выполнения операций
def apply_operation(a, b, operation):
    if operation == "sum":
        return a + b
    elif operation == "sub":
        return a - b
    elif operation == "mul":
        return a * b
    elif operation == "div":
        return a / b if b != 0 else 0
    else:
        raise ValueError(f"Неизвестная операция: {operation}")

# 1. GET-запрос
get_num = random.randint(1, 10)
get_response = requests.get(
    "http://localhost:5000/number/",
    params={"param": get_num}
)
get_data = get_response.json()
num1, op1 = get_data["number"], get_data["operation"]
print(f"GET: num={num1}, operation={op1}")

# 2. POST-запрос
post_num = random.randint(1, 10)
post_response = requests.post(
    "http://localhost:5000/number/",
    json={"jsonParam": post_num},
    headers={"Content-Type": "application/json"}
)
post_data = post_response.json()
num2, op2 = post_data["number"], post_data["operation"]
print(f"POST: num={num2}, operation={op2}")

# 3. DELETE-запрос
delete_response = requests.delete("http://localhost:5000/number/")
delete_data = delete_response.json()
num3, op3 = delete_data["number"], delete_data["operation"]
print(f"DELETE: num={num3}, operation={op3}")

# 4. Вычисление результата
try:
    # Выполняем операции последовательно: ((num1 OP2 num2) OP3 num3)
    intermediate = apply_operation(num1, num2, op2)
    final_result = apply_operation(intermediate, num3, op3)
    final_result = int(final_result)
except Exception as e:
    final_result = f"Ошибка: {str(e)}"

print(f"\nРезультат: {final_result}")