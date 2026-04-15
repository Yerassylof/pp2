-- 1. Insert or update user
CREATE OR REPLACE PROCEDURE upsert_user(p_name TEXT, p_phone TEXT)
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM phonebook WHERE name = p_name) THEN
        UPDATE phonebook
        SET phone = p_phone
        WHERE name = p_name;
    ELSE
        INSERT INTO phonebook(name, phone)
        VALUES (p_name, p_phone);
    END IF;
END;
$$;


-- 2. Bulk insert with validation + return incorrect data via refcursor
CREATE OR REPLACE PROCEDURE bulk_insert_users(
    users TEXT[][],
    INOUT bad_cursor REFCURSOR DEFAULT 'bad_users'
)
LANGUAGE plpgsql
AS $$
DECLARE
    i INT;
    uname TEXT;
    uphone TEXT;
BEGIN
    CREATE TEMP TABLE IF NOT EXISTS bad_data(
        name TEXT,
        phone TEXT,
        reason TEXT
    ) ON COMMIT DROP;

    FOR i IN array_lower(users, 1)..array_upper(users, 1) LOOP
        uname := users[i][1];
        uphone := users[i][2];

        IF uphone ~ '^[0-9+]{7,15}$' THEN
            INSERT INTO phonebook(name, phone)
            VALUES (uname, uphone);
        ELSE
            INSERT INTO bad_data(name, phone, reason)
            VALUES (uname, uphone, 'Invalid phone format');
        END IF;
    END LOOP;

    OPEN bad_cursor FOR SELECT * FROM bad_data;
END;
$$;


-- 3. Delete by name or phone
CREATE OR REPLACE PROCEDURE delete_contact(p_value TEXT)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM phonebook
    WHERE name = p_value OR phone = p_value;
END;
$$;