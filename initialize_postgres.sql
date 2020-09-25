
CREATE ROLE sympa;
-- [..omissis.. ] give him access hba.conf....
GRANT CONNECT ON DATABASE obvious_db TO sympa WITH PASSWORD 'youknowwhatitis';
-- This assumes you're actually connected to obvious_db..
GRANT USAGE ON SCHEMA exixting_schema TO sympa;
ALTER ROLE sympa SET search_path TO exixting_schema;

CREATE VIEW lit_mailing_list_v AS
SELECT * from AD_USER

GRANT SELECT ON lit_mailing_list_v TO sympa;



