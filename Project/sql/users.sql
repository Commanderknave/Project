DROP TABLE IF EXISTS users;

CREATE TABLE users(
	user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(30) NOT NULL,
    user_password VARCHAR(255) NOT NULL,
    creation_date TIMESTAMP,
    last_login TIMESTAMP
)