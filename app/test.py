receipt_number = 0
items_count = 0
total_price = 0


def add_item(item_name, item_price):
    global items_count
    items_count += 1
    global total_price
    total_price += item_price

def print_receipt():
    global receipt_number
    receipt_number += 1
    global items_count
    global total_price
    print(f'Чек {receipt_number} Всего предметов: {items_count}\n{item_name} - {item_price}\nИтого: {total_price} руб.\n')
    
add_item('Блокнот', 100)
print_receipt()

add_item('Ручка', 70)
print_receipt()
print_receipt()

add_item('Булочка', 15)
add_item('Булочка', 15)
add_item('Чай', 5)
print_receipt()

add_item('Булочка', 15)
add_item('Булочка', 15)