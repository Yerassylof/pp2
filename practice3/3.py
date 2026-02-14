str_base = ["ONE", "TWO", "THR", "FOU", "FIV", "SIX", "SEV", "EIG", "NIN", "ZER"] # six seveeeen 02.02.2026 12:26
int_base = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
int_with_str_base = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']

def find_oper(string):
    for char in string:
        if char == "+" or char == "-" or char == "/" or char == "*":
            global oper
            oper = char
            global oper_pos
            oper_pos = string.index(char)
            break

def transfer_to_integed_str(part_of_string):
    return int_with_str_base[str_base.index(part_of_string)]

def constructing_parts(string):
    first_part = ""
    second_part = ""
    for i in range(0, oper_pos, 3):
        current_val = string[i:i+3]
        current_int_with_str_val = transfer_to_integed_str(current_val)
        first_part = first_part + current_int_with_str_val

    for i in range(oper_pos + 1, len(full_string), 3):
        current_val = string[i:i+3]
        current_int_with_str_val = transfer_to_integed_str(current_val)
        second_part = second_part + current_int_with_str_val
    return first_part, second_part

def expression(first_val, second_val, operator):
    if operator == "+":
        return int(first_val) + int(second_val)
    elif operator == "-":
        return int(first_val) - int(second_val)
    elif operator == "*":
        return int(first_val) * int(second_val)
    else:
        return int(first_val) / int(second_val)

def cout_result(int_result):
    str_result = str(int_result)
    result = ""
    for char in str_result:
        result = result + str_base[int_with_str_base.index(char)]
    return result


full_string = input()
find_oper(full_string)
first_val, second_val = constructing_parts(full_string)
int_result = expression(first_val, second_val, oper)

print(cout_result(int_result))