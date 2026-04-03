import csv
from connect import get_connection

conn = get_connection()
cur = conn.cursor()


def add_contact(name, phone):
    cur.execute("INSERT INTO phonebook (name, phone) VALUES (%s, %s)", (name, phone))
    conn.commit()
    print(f"Contact {name} added.")


def add_contacts_from_csv(filename):
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            add_contact(row[0], row[1])


def update_contact(old_name, new_name=None, new_phone=None):
    if new_name:
        cur.execute("UPDATE phonebook SET name=%s WHERE name=%s", (new_name, old_name))
    if new_phone:
        cur.execute("UPDATE phonebook SET phone=%s WHERE name=%s", (new_phone, old_name))
    conn.commit()
    print(f"Contact {old_name} updated.")


def search_contact(name=None, phone_prefix=None):
    query = "SELECT name, phone FROM phonebook WHERE TRUE"
    params = []
    if name:
        query += " AND name ILIKE %s"
        params.append(f"%{name}%")
    if phone_prefix:
        query += " AND phone LIKE %s"
        params.append(f"{phone_prefix}%")
    cur.execute(query, tuple(params))
    return cur.fetchall()


def delete_contact(name=None, phone=None):
    if name:
        cur.execute("DELETE FROM phonebook WHERE name=%s", (name,))
    elif phone:
        cur.execute("DELETE FROM phonebook WHERE phone=%s", (phone,))
    conn.commit()
    print("Contact deleted.")