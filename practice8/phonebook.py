from connect import get_connection

def call_function(func_name, params=()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {func_name}(%s)", params)
    rows = cur.fetchall()
    for r in rows:
        print(r)
    cur.close()
    conn.close()

def call_procedure(proc_name, params=()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"CALL {proc_name}(%s, %s)", params)
    conn.commit()
    cur.close()
    conn.close()