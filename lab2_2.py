# Считываем строку с клавиатуры
input_string = input("Введите строку: ")

result = []
for char in input_string:
    if 'А' <= char <= 'Я':
        
        lower_char = chr(ord(char) + 32)
        result.append(lower_char)
    elif 'A' <= char <= 'Z':
            lower_char = chr(ord(char) + 32)
            result.append(lower_char)
    else:
        result.append(char)
        
  

output_string = ''.join(result)

print("Результат:", output_string)