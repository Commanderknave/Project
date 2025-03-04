DROP TABLE IF EXISTS wished_games;

CREATE TABLE wished_games(
	game_id INT NOT NULL,
    user_id INT NOT NULL,
    purchased BOOLEAN DEFAULT FALSE,
	FOREIGN KEY (game_id) REFERENCES games,
    FOREIGN KEY (user_id) REFERENCES users,
    PRIMARY KEY (game_id, user_id)
)