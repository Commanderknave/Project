DELIMITER //

DROP PROCEDURE IF EXISTS registerUser //
CREATE PROCEDURE registerUser(
	IN username VARCHAR(30), 
    IN user_password VARCHAR(255)
)
BEGIN
	INSERT INTO users (username, user_password, creation_date)
		VALUES (username, user_password, CURRENT_TIMESTAMP());
	SELECT * FROM users WHERE users.username=username;
END //

DROP PROCEDURE IF EXISTS deleteUser //
CREATE PROCEDURE deleteUser(
	IN user_id_in INT
)
BEGIN
	DELETE FROM users WHERE user_id=user_id_in;
END //

DROP PROCEDURE IF EXISTS preValidateUser //
CREATE PROCEDURE preValidateUser(
	IN user_id INT,
    IN email VARCHAR(255),
    IN email_hash TEXT
)
BEGIN
	INSERT INTO verified_emails (user_id,email,email_hash, verification_time, email_send_time)
		VALUES (user_id,email,email_hash,FROM_UNIXTIME(1),NOW());
END //

DROP PROCEDURE IF EXISTS resetValidationTime //
CREATE PROCEDURE resetValidationTime(
	IN hash_in VARCHAR(255)
)
BEGIN
	UPDATE verified_emails SET email_send_time=NOW() WHERE email_hash=hash_in;
    SELECT * FROM verified_emails WHERE email_hash=hash_in;
END //

DROP PROCEDURE IF EXISTS validateUser //
CREATE PROCEDURE validateUser(
    IN hash_in VARCHAR(255)
)
BEGIN
	DECLARE send_time TIMESTAMP;
    SELECT email_send_time INTO send_time FROM verified_emails WHERE email_hash=hash_in;
	IF TIMESTAMPDIFF(SECOND,send_time,NOW())>1800 THEN
		SIGNAL SQLSTATE '45000'
		SET MESSAGE_TEXT = 'Token Expired';
    ELSE
		UPDATE verified_emails SET verification_time=NOW() WHERE email_hash=hash_in;
	END IF;
END //

DROP PROCEDURE IF EXISTS invalidateUser //
CREATE PROCEDURE invalidateUser(
	IN user_id_in INT
)
BEGIN
	UPDATE verified_emails SET verification_time=FROM_UNIXTIME(1) WHERE user_id=user_id_in;
END //

DROP PROCEDURE IF EXISTS getUserEmail //
CREATE PROCEDURE getUserEmail(
	IN user_id_in INT
)
BEGIN
	SELECT * FROM verified_emails WHERE user_id=user_id_in;
END //

DROP PROCEDURE IF EXISTS updatePassword //
CREATE PROCEDURE updatePassword(
	IN user_id_in INT,
    IN new_password VARCHAR(255)
)
BEGIN
	UPDATE users SET user_password=new_password WHERE user_id=user_id_in;
END //

DROP PROCEDURE IF EXISTS loginUser //
CREATE PROCEDURE loginUser(
	IN username_in VARCHAR(30),
    IN user_password_in VARCHAR(255)
)
BEGIN
	SELECT * FROM users
		INNER JOIN verified_emails ON users.user_id=verified_emails.user_id
		WHERE username=username_in 
			AND user_password=user_password_in
            AND verified_emails.verification_time !=FROM_UNIXTIME(1);
	IF (FOUND_ROWS()=1) THEN
		UPDATE users SET last_login=NOW() WHERE username=username_in;
        SELECT user_id FROM users where username=username_in;
	END IF;
END //

DROP PROCEDURE IF EXISTS fetchUser //
CREATE PROCEDURE fetchUser(
	IN id INT
)
BEGIN
	SELECT user_id, username, creation_date, last_login
		FROM users WHERE user_id=id;
END //

DROP PROCEDURE IF EXISTS fetchUserByName //
CREATE PROCEDURE fetchUserByName(
	IN username_in VARCHAR(30)
)
BEGIN
	SELECT user_id, username, creation_date, last_login
		FROM users WHERE username LIKE CONCAT('%',username_in,'%');
END //

DROP PROCEDURE IF EXISTS addGame //
CREATE PROCEDURE addGame(
	IN url TEXT,
    IN steam_id INT,
    IN game_name VARCHAR(255),
    IN developer VARCHAR(255),
    IN publisher VARCHAR(255),
    IN release_date DATE,
    IN price TEXT,
    IN game_description TEXT,
    IN thumbnail TEXT
)
BEGIN
	INSERT INTO games (url, steam_id, game_name, developer, publisher, 
						release_date, price, game_description, thumbnail)
		VALUES (url, steam_id, game_name, developer, publisher, 
				release_date, price, game_description, thumbnail);
END //

DROP PROCEDURE IF EXISTS fetchGame //
CREATE PROCEDURE fetchGame(
	IN id INT
)
BEGIN
	SELECT * FROM games WHERE game_id=id;
END //
DROP PROCEDURE IF EXISTS fetchGameByName //
CREATE PROCEDURE fetchGameByName(
	IN game_name_in VARCHAR(50)
)
BEGIN
	SELECT * FROM games WHERE game_name LIKE CONCAT('%',game_name_in,'%');
END //

DROP PROCEDURE IF EXISTS wishGame //
CREATE PROCEDURE wishGame(
	IN user_id INT,
    IN game_id INT
)
BEGIN
	INSERT INTO wished_games (user_id, game_id, purchased) VALUES (user_id,game_id, False);
END //

DROP PROCEDURE IF EXISTS unwishGame //
CREATE PROCEDURE unwishGame(
	IN user_id_in INT,
    IN game_id_in INT
)
BEGIN
	DELETE FROM wished_games where user_id=user_id_in AND game_id=game_id_in;
END //

DROP PROCEDURE IF EXISTS fetchUserWishlist //
CREATE PROCEDURE fetchUserWishlist(
	IN user_id_in INT
)
BEGIN
	SELECT games.*, wished_games.purchased FROM games INNER JOIN wished_games ON games.game_id=wished_games.game_id WHERE user_id=user_id_in;
END //

DROP PROCEDURE IF EXISTS purchaseGame //
CREATE PROCEDURE purchaseGame(
	IN user_id_in INT,
    IN game_id_in INT
)
BEGIN
	UPDATE wished_games SET purchased=TRUE WHERE user_id=user_id_in AND game_id=game_id_in;
END //

DELIMITER ;