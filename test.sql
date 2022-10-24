CREATE TABLE history (
	contact_id INTEGER PRIMARY KEY,
	first_name TEXT NOT NULL,
	last_name TEXT NOT NULL,
	email TEXT NOT NULL UNIQUE,
	phone TEXT NOT NULL UNIQUE
);

CREATE TABLE contacts (
	contact_id INTEGER PRIMARY KEY,
	first_name TEXT NOT NULL,
	last_name TEXT NOT NULL,
	email TEXT NOT NULL UNIQUE,
	phone TEXT NOT NULL UNIQUE
);


CREATE TABLE history (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    userid INTEGER NOT NULL,
    symbol TEXT NOT NULL,
    shares FLOAT NOT NULL,
    amout FLOAT NOT NULL,
    trantype TEXT NOT NULL,
    FOREIGN KEY (userid)
        REFERENCES users(id)
);

CREATE TABLE genre (
	id INTEGER PRIMARY KEY,
	genre TEXT NOT NULL
)

INSERT INTO bookusers (username,hash)
VALUES (
	"opxz7148",
	"pbkdf2:sha256:260000$WNjsfzYiOqnbRkiQ$cb46202f69ed582c461d4b332a8dcc245ac326e741ae3d455b78dbdb38ba769d"
)

INSERT INTO genre (genre) VALUES
(
	"Science Fiction"
)

INSERT INTO genre (genre) VALUES
(
	"Drama"
);

CREATE TABLE user_genre (
	userid INTEGER,
	genreid INTEGER
)

CREATE TABLE users_book
(
	userid INTEGER NOT NULL,
	bookid INTEGER NOT NULL,
	status TEXT NOT NULL,
	FOREIGN KEY (userid) REFERENCES bookusers(id),
	FOREIGN KEY (bookid) REFERENCES book(booknoid)
)

CREATE TABLE book
(
	booknoid INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	bookgid TEXT NOT NULL UNIQUE,
	imglink TEXT NOT NULL,
	title TEXT NOT NULL,
	authors TEXT NOT NULL
)

CREATE TABLE book
(
	booknoid INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	bookgid TEXT NOT NULL UNIQUE,
	imglink TEXT NOT NULL,
	title TEXT NOT NULL,
	authors TEXT NOT NULL
)