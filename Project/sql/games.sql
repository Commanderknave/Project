DROP TABLE IF EXISTS games;

CREATE TABLE games(
	game_id INT AUTO_INCREMENT PRIMARY KEY,
    url TEXT NOT NULL,
	steam_id INT NOT NULL,
    game_name VARCHAR(255),
    developer VARCHAR(255),
    publisher VARCHAR(255),
    release_date DATE,
    price DECIMAL(10,2) UNSIGNED,
    game_description TEXT,
    thumbnail TEXT
)