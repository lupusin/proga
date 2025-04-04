#Задание 1.1
def get_number(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Ошибка: введите число!")

a = get_number("Введите первое число: ")
b = get_number("Введите второе число: ")
c = get_number("Введите третье число: ")

min_num = min(a, b, c)
print("Минимальное число:", min_num)