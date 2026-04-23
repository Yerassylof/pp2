import psycopg2
import csv
import json
import os
from datetime import datetime
from connect import get_connection

# ──────────────────────────────────────────────
# DATABASE SETUP
# ──────────────────────────────────────────────

def setup_database():
    """Run schema.sql and procedures.sql to initialize the database."""
    conn = get_connection()
    cur = conn.cursor()
    base = os.path.dirname(__file__)
    for filename in ["schema.sql", "procedures.sql"]:
        path = os.path.join(base, filename)
        with open(path, "r", encoding="utf-8") as f:
            cur.execute(f.read())
    conn.commit()
    cur.close()
    conn.close()
    print("Database setup complete.")

# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────

def get_group_id(cur, group_name):
    """Return group id by name, or None."""
    cur.execute("SELECT id FROM groups WHERE name ILIKE %s", (group_name,))
    row = cur.fetchone()
    return row[0] if row else None

def print_contacts(rows):
    """Pretty-print contact rows returned from DB functions."""
    if not rows:
        print("  (no contacts found)")
        return
    print(f"\n{'ID':<5} {'Name':<20} {'Email':<25} {'Birthday':<12} {'Group':<10} {'Phones'}")
    print("-" * 90)
    for r in rows:
        cid, name, email, birthday, grp, phones = r
        print(f"{cid:<5} {str(name):<20} {str(email or ''):<25} "
              f"{str(birthday or ''):<12} {str(grp or ''):<10} {phones or ''}")
    print()

# ──────────────────────────────────────────────
# CRUD
# ──────────────────────────────────────────────

def add_contact():
    """Add a new contact with multiple phones interactively."""
    print("\n── Add Contact ──")
    name     = input("Name: ").strip()
    email    = input("Email (optional): ").strip() or None
    birthday = input("Birthday (YYYY-MM-DD, optional): ").strip() or None
    print("Groups: Family, Work, Friend, Other")
    group    = input("Group (optional): ").strip() or None

    conn = get_connection()
    cur  = conn.cursor()

    group_id = get_group_id(cur, group) if group else None

    cur.execute(
        "INSERT INTO contacts (name, email, birthday, group_id) VALUES (%s,%s,%s,%s) RETURNING id",
        (name, email, birthday, group_id)
    )
    contact_id = cur.fetchone()[0]

    # Add phones
    while True:
        phone = input("Phone number (or Enter to stop): ").strip()
        if not phone:
            break
        ptype = input("Type (home/work/mobile): ").strip().lower()
        if ptype not in ("home", "work", "mobile"):
            ptype = "mobile"
        cur.execute(
            "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
            (contact_id, phone, ptype)
        )

    conn.commit()
    cur.close()
    conn.close()
    print(f"Contact '{name}' added with ID {contact_id}.")

def delete_contact():
    """Delete contact by name or phone."""
    print("\n── Delete Contact ──")
    value = input("Enter name or phone to delete: ").strip()
    conn  = get_connection()
    cur   = conn.cursor()

    # Try by name first
    cur.execute("DELETE FROM contacts WHERE name ILIKE %s RETURNING id", (value,))
    deleted = cur.fetchall()
    if not deleted:
        # Try by phone
        cur.execute("""
            DELETE FROM contacts WHERE id IN (
                SELECT contact_id FROM phones WHERE phone = %s
            ) RETURNING id
        """, (value,))
        deleted = cur.fetchall()

    conn.commit()
    cur.close()
    conn.close()
    print(f"Deleted {len(deleted)} contact(s).")

def update_contact():
    """Update contact email, birthday, or group."""
    print("\n── Update Contact ──")
    name = input("Contact name to update: ").strip()
    conn = get_connection()
    cur  = conn.cursor()

    cur.execute("SELECT id FROM contacts WHERE name ILIKE %s LIMIT 1", (name,))
    row = cur.fetchone()
    if not row:
        print("Contact not found.")
        cur.close(); conn.close(); return

    contact_id = row[0]
    email    = input("New email (Enter to skip): ").strip() or None
    birthday = input("New birthday YYYY-MM-DD (Enter to skip): ").strip() or None
    group    = input("New group (Enter to skip): ").strip() or None

    if email:
        cur.execute("UPDATE contacts SET email=%s WHERE id=%s", (email, contact_id))
    if birthday:
        cur.execute("UPDATE contacts SET birthday=%s WHERE id=%s", (birthday, contact_id))
    if group:
        group_id = get_group_id(cur, group)
        if group_id:
            cur.execute("UPDATE contacts SET group_id=%s WHERE id=%s", (group_id, contact_id))
        else:
            print(f"Group '{group}' not found.")

    conn.commit()
    cur.close(); conn.close()
    print("Contact updated.")

# ──────────────────────────────────────────────
# SEARCH & FILTER
# ──────────────────────────────────────────────

def search_contacts():
    """Search contacts by name, phone, or email using DB function."""
    query = input("Search query: ").strip()
    conn  = get_connection()
    cur   = conn.cursor()
    cur.execute("SELECT * FROM search_contacts(%s)", (query,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    print_contacts(rows)

def filter_by_group():
    """Show contacts filtered by group."""
    print("\nGroups: Family, Work, Friend, Other")
    group = input("Group name: ").strip()
    conn  = get_connection()
    cur   = conn.cursor()
    cur.execute("""
        SELECT c.id, c.name, c.email, c.birthday, g.name,
               STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ')
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON p.contact_id = c.id
        WHERE g.name ILIKE %s
        GROUP BY c.id, c.name, c.email, c.birthday, g.name
        ORDER BY c.name
    """, (group,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    print_contacts(rows)

def search_by_email():
    """Partial email search."""
    query = input("Email search (e.g. gmail): ").strip()
    conn  = get_connection()
    cur   = conn.cursor()
    cur.execute("""
        SELECT c.id, c.name, c.email, c.birthday, g.name,
               STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ')
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON p.contact_id = c.id
        WHERE c.email ILIKE %s
        GROUP BY c.id, c.name, c.email, c.birthday, g.name
    """, (f"%{query}%",))
    rows = cur.fetchall()
    cur.close(); conn.close()
    print_contacts(rows)

def sort_contacts():
    """Sort and display contacts."""
    print("Sort by: 1) name  2) birthday  3) date added")
    choice = input("Choice: ").strip()
    order  = {"1": "c.name", "2": "c.birthday", "3": "c.created_at"}.get(choice, "c.name")
    conn   = get_connection()
    cur    = conn.cursor()
    cur.execute(f"""
        SELECT c.id, c.name, c.email, c.birthday, g.name,
               STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ')
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON p.contact_id = c.id
        GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
        ORDER BY {order}
    """)
    rows = cur.fetchall()
    cur.close(); conn.close()
    print_contacts(rows)

def paginated_view():
    """Navigate contacts page by page."""
    page_size = 5
    offset    = 0
    conn      = get_connection()
    cur       = conn.cursor()

    while True:
        cur.execute("SELECT * FROM get_contacts_page(%s, %s)", (page_size, offset))
        rows = cur.fetchall()
        print_contacts(rows)
        print(f"Page {offset // page_size + 1} | Commands: next / prev / quit")
        cmd = input(">> ").strip().lower()
        if cmd == "next":
            if len(rows) == page_size:
                offset += page_size
            else:
                print("Already on last page.")
        elif cmd == "prev":
            offset = max(0, offset - page_size)
        elif cmd == "quit":
            break

    cur.close(); conn.close()

# ──────────────────────────────────────────────
# STORED PROCEDURE CALLS
# ──────────────────────────────────────────────

def call_add_phone():
    """Call add_phone stored procedure."""
    name  = input("Contact name: ").strip()
    phone = input("Phone number: ").strip()
    ptype = input("Type (home/work/mobile): ").strip().lower()
    conn  = get_connection()
    cur   = conn.cursor()
    try:
        cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, ptype))
        conn.commit()
        print("Phone added.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cur.close(); conn.close()

def call_move_to_group():
    """Call move_to_group stored procedure."""
    name  = input("Contact name: ").strip()
    group = input("Group name: ").strip()
    conn  = get_connection()
    cur   = conn.cursor()
    try:
        cur.execute("CALL move_to_group(%s, %s)", (name, group))
        conn.commit()
        print(f"Moved '{name}' to group '{group}'.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cur.close(); conn.close()

# ──────────────────────────────────────────────
# IMPORT / EXPORT
# ──────────────────────────────────────────────

def export_to_json():
    """Export all contacts to contacts_export.json."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT c.id, c.name, c.email,
               TO_CHAR(c.birthday, 'YYYY-MM-DD'), g.name,
               JSON_AGG(
                   JSON_BUILD_OBJECT('phone', p.phone, 'type', p.type)
               ) FILTER (WHERE p.phone IS NOT NULL)
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON p.contact_id = c.id
        GROUP BY c.id, c.name, c.email, c.birthday, g.name
        ORDER BY c.name
    """)
    rows = cur.fetchall()
    cur.close(); conn.close()

    contacts = []
    for r in rows:
        contacts.append({
            "id":       r[0],
            "name":     r[1],
            "email":    r[2],
            "birthday": r[3],
            "group":    r[4],
            "phones":   r[5] or []
        })

    path = os.path.join(os.path.dirname(__file__), "contacts_export.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(contacts, f, ensure_ascii=False, indent=2)
    print(f"Exported {len(contacts)} contacts to '{path}'.")

def import_from_json():
    """Import contacts from a JSON file."""
    path = input("JSON file path (default: contacts_export.json): ").strip()
    if not path:
        path = os.path.join(os.path.dirname(__file__), "contacts_export.json")

    with open(path, "r", encoding="utf-8") as f:
        contacts = json.load(f)

    conn = get_connection()
    cur  = conn.cursor()

    for c in contacts:
        name = c.get("name", "").strip()
        if not name:
            continue

        # Check duplicate
        cur.execute("SELECT id FROM contacts WHERE name ILIKE %s LIMIT 1", (name,))
        existing = cur.fetchone()

        if existing:
            choice = input(f"'{name}' already exists. (s)kip / (o)verwrite? ").strip().lower()
            if choice != "o":
                continue
            cur.execute("DELETE FROM contacts WHERE id=%s", (existing[0],))

        # Get group id
        group_id = get_group_id(cur, c.get("group", "")) if c.get("group") else None

        cur.execute(
            "INSERT INTO contacts (name, email, birthday, group_id) VALUES (%s,%s,%s,%s) RETURNING id",
            (name, c.get("email"), c.get("birthday"), group_id)
        )
        contact_id = cur.fetchone()[0]

        for ph in (c.get("phones") or []):
            cur.execute(
                "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                (contact_id, ph.get("phone"), ph.get("type"))
            )

    conn.commit()
    cur.close(); conn.close()
    print("JSON import complete.")

def import_from_csv():
    """Import contacts from CSV with extended fields."""
    path = input("CSV file path (default: contacts.csv): ").strip()
    if not path:
        path = os.path.join(os.path.dirname(__file__), "contacts.csv")

    conn = get_connection()
    cur  = conn.cursor()
    count = 0

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name  = row.get("name", "").strip()
            if not name:
                continue

            email    = row.get("email", "").strip() or None
            birthday = row.get("birthday", "").strip() or None
            group    = row.get("group", "").strip() or None
            phone    = row.get("phone", "").strip() or None
            ptype    = row.get("type", "mobile").strip().lower()

            group_id = get_group_id(cur, group) if group else None

            # Upsert contact
            cur.execute("SELECT id FROM contacts WHERE name ILIKE %s LIMIT 1", (name,))
            existing = cur.fetchone()
            if existing:
                contact_id = existing[0]
                cur.execute(
                    "UPDATE contacts SET email=%s, birthday=%s, group_id=%s WHERE id=%s",
                    (email, birthday, group_id, contact_id)
                )
            else:
                cur.execute(
                    "INSERT INTO contacts (name, email, birthday, group_id) VALUES (%s,%s,%s,%s) RETURNING id",
                    (name, email, birthday, group_id)
                )
                contact_id = cur.fetchone()[0]

            if phone:
                cur.execute(
                    "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                    (contact_id, phone, ptype)
                )
            count += 1

    conn.commit()
    cur.close(); conn.close()
    print(f"CSV import complete: {count} record(s) processed.")

# ──────────────────────────────────────────────
# MAIN MENU
# ──────────────────────────────────────────────

def main():
    print("Initializing database...")
    setup_database()

    menu = """
╔══════════════════════════════════════╗
║       PhoneBook Extended Menu        ║
╠══════════════════════════════════════╣
║  1. Add contact                      ║
║  2. Delete contact                   ║
║  3. Update contact                   ║
║  4. Search contacts                  ║
║  5. Filter by group                  ║
║  6. Search by email                  ║
║  7. Sort contacts                    ║
║  8. Paginated view                   ║
║  9. Add phone (stored proc)          ║
║ 10. Move to group (stored proc)      ║
║ 11. Export to JSON                   ║
║ 12. Import from JSON                 ║
║ 13. Import from CSV                  ║
║  0. Exit                             ║
╚══════════════════════════════════════╝"""

    actions = {
        "1":  add_contact,
        "2":  delete_contact,
        "3":  update_contact,
        "4":  search_contacts,
        "5":  filter_by_group,
        "6":  search_by_email,
        "7":  sort_contacts,
        "8":  paginated_view,
        "9":  call_add_phone,
        "10": call_move_to_group,
        "11": export_to_json,
        "12": import_from_json,
        "13": import_from_csv,
    }

    while True:
        print(menu)
        choice = input("Choose option: ").strip()
        if choice == "0":
            print("Goodbye!")
            break
        elif choice in actions:
            try:
                actions[choice]()
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()