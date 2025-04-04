import sys

def main():
    # 1. Считываем массив из аргументов командной строки (пропускаем имя скрипта)
    if len(sys.argv) < 2:
        print("Ошибка: не переданы элементы массива!")
        return
    
    try:
        arr = list(map(int, sys.argv[1:]))
    except ValueError:
        print("Ошибка: все элементы должны быть целыми числами!")
        return

    print("Исходный массив:", arr)

    # 2. Выводим пары отрицательных чисел, стоящих рядом
    print("\nПары отрицательных чисел, стоящих рядом:")
    found_pairs = False
    for i in range(len(arr) - 1):
        if arr[i] < 0 and arr[i + 1] < 0:
            print(f"({arr[i]}, {arr[i + 1]})")
            found_pairs = True
    if not found_pairs:
        print("Таких пар нет.")

    # 3. Удаляем все повторяющиеся числа (оставляем только уникальные)
    unique_arr = []
    seen = set()
    for num in arr:
        if num not in seen:
            seen.add(num)
            unique_arr.append(num)

    # 4. Выводим полученный массив без дубликатов
    print("\nМассив без повторяющихся чисел:", unique_arr)

if __name__ == "__main__":
    main()