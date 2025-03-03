DROP TABLE IF EXISTS verified_emails;
DROP TABLE IF EXISTS user_settings;
DROP TABLE IF EXISTS friends;
DROP TABLE IF EXISTS wished_games;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS users;

SOURCE users.sql
SOURCE user_settings.sql
SOURCE verified_emails.sql
SOURCE friends.sql
SOURCE games.sql
SOURCE wished_games.sql