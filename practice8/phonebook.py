import psycopg2
from config import load_config


def get_connection():
    return psycopg2.connect(**load_config())


# Call search function
def search(pattern):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM search_phonebook(%s)", (pattern,))
    rows = cur.fetchall()

    cur.close()
    conn.close()
    return rows


# Insert or update user
def upsert_user(name, phone):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("CALL upsert_user(%s, %s)", (name, phone))

    conn.commit()
    cur.close()
    conn.close()


# Bulk insert
def bulk_insert(users):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("CALL bulk_insert_users(%s, 'bad_users')", (users,))

    cur.execute("FETCH ALL FROM bad_users")
    bad_data = cur.fetchall()

    conn.commit()
    cur.close()
    conn.close()

    return bad_data


# Pagination function
def get_paginated(limit, offset):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM get_phonebook_paginated(%s, %s)", (limit, offset))
    rows = cur.fetchall()

    cur.close()
    conn.close()
    return rows


# Delete user
def delete_contact(value):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("CALL delete_contact(%s)", (value,))

    conn.commit()
    cur.close()
    conn.close()