DROP TABLE IF EXISTS verified_emails;

CREATE TABLE verified_emails(
	user_id INT PRIMARY KEY,
	email VARCHAR(255),
    verification_time TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users
)