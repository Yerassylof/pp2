-- 1. Add phone to existing contact
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone        VARCHAR,
    p_type         VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN
    SELECT id INTO v_contact_id
    FROM contacts WHERE name ILIKE p_contact_name LIMIT 1;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found', p_contact_name;
    END IF;

    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type);

    RAISE NOTICE 'Phone added to contact "%"', p_contact_name;
END;
$$;

-- 2. Move contact to group (create group if not exists)
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name   VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
    v_group_id   INTEGER;
BEGIN
    -- Get or create group
    INSERT INTO groups (name) VALUES (p_group_name)
    ON CONFLICT (name) DO NOTHING;

    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;
    SELECT id INTO v_contact_id FROM contacts WHERE name ILIKE p_contact_name LIMIT 1;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found', p_contact_name;
    END IF;

    UPDATE contacts SET group_id = v_group_id WHERE id = v_contact_id;
    RAISE NOTICE 'Contact "%" moved to group "%"', p_contact_name, p_group_name;
END;
$$;

-- 3. Search contacts by name, phone, or email
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    id       INTEGER,
    name     VARCHAR,
    email    VARCHAR,
    birthday DATE,
    grp      VARCHAR,
    phones   TEXT
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT
        c.id,
        c.name,
        c.email,
        c.birthday,
        g.name AS grp,
        STRING_AGG(p.phone || ' (' || COALESCE(p.type, '?') || ')', ', ') AS phones
    FROM contacts c
    LEFT JOIN groups g ON c.group_id = g.id
    LEFT JOIN phones p ON p.contact_id = c.id
    WHERE
        c.name  ILIKE '%' || p_query || '%' OR
        c.email ILIKE '%' || p_query || '%' OR
        p.phone ILIKE '%' || p_query || '%'
    GROUP BY c.id, c.name, c.email, c.birthday, g.name;
END;
$$;

-- 4. Paginated query function (from Practice 8, kept for reference)
CREATE OR REPLACE FUNCTION get_contacts_page(p_limit INT, p_offset INT)
RETURNS TABLE (
    id       INTEGER,
    name     VARCHAR,
    email    VARCHAR,
    birthday DATE,
    grp      VARCHAR,
    phones   TEXT
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.name,
        c.email,
        c.birthday,
        g.name AS grp,
        STRING_AGG(p.phone || ' (' || COALESCE(p.type, '?') || ')', ', ') AS phones
    FROM contacts c
    LEFT JOIN groups g ON c.group_id = g.id
    LEFT JOIN phones p ON p.contact_id = c.id
    GROUP BY c.id, c.name, c.email, c.birthday, g.name
    ORDER BY c.name
    LIMIT p_limit OFFSET p_offset;
END;
$$;