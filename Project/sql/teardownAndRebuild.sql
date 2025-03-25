DROP TABLE IF EXISTS verified_emails;
DROP TABLE IF EXISTS wished_games;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS users;

SOURCE users.sql
SOURCE user_settings.sql
SOURCE verified_emails.sql
SOURCE games.sql
SOURCE wished_games.sql
SOURCE procedures.sql