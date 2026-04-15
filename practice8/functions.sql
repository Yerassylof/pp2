-- 1. Search function (name / surname / phone pattern)
CREATE OR REPLACE FUNCTION search_phonebook(pattern TEXT)
RETURNS TABLE(id INT, name TEXT, phone TEXT)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT p.id, p.name, p.phone
    FROM phonebook p
    WHERE p.name ILIKE '%' || pattern || '%'
       OR p.phone ILIKE '%' || pattern || '%';
END;
$$;


-- 2. Pagination function
CREATE OR REPLACE FUNCTION get_phonebook_paginated(limit_val INT, offset_val INT)
RETURNS TABLE(id INT, name TEXT, phone TEXT)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT p.id, p.name, p.phone
    FROM phonebook p
    ORDER BY p.id
    LIMIT limit_val OFFSET offset_val;
END;
$$;