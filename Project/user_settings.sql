DROP TABLE IF EXISTS user_settings;

CREATE TABLE user_settings(
	user_id INT PRIMARY KEY,
    FOREIGN KEY (user_id) REFERENCES users
) 