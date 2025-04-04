#Задание 1.1
# def get_number(prompt):
#     while True:
#         try:
#             return float(input(prompt))
#         except ValueError:
#             print("Ошибка: введите число!")

# a = get_number("Введите первое число: ")
# b = get_number("Введите второе число: ")
# c = get_number("Введите третье число: ")

# min_num = min(a, b, c)
# print("Минимальное число:", min_num)

#Задание 1.2
# def get_number(prompt):
#     while True:
#         try:
#             return float(input(prompt))
#         except ValueError:
#             print("Ошибка: введите число!")

# nums = [get_number(f"Введите число {i+1}: ") for i in range(3)]

# print("Числа в интервале [1, 50]:")
# for num in nums:
#     if 1 <= num <= 50:
#         print(num)

#Задание 1.3
def get_number(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Ошибка: введите число!")

m = get_number("Введите вещественное число m: ")

print("Последовательность:")
for i in range(1, 11):
    print(i * m)