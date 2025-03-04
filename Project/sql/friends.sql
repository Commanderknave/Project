DROP TABLE IF EXISTS friends;

CREATE TABLE friends(
	friender INT,
    friendee INT,
    FOREIGN KEY (friender) REFERENCES users (user_id),
    FOREIGN KEY (friendee) REFERENCES users (user_id),
    PRIMARY KEY (friender,friendee)
)