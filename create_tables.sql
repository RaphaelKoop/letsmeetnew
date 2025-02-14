--  Vorhandene Tabellen löschen
DROP TABLE IF EXISTS
    user_hobby_preferences,
    user_hobbies,
    friendships,
    messages,
    likes,
    conversations,
    user_photos,
    hobbies,
    users,
    addresses,
    user_images
CASCADE;


--  Adresse-Tabelle (Anschriften)
CREATE TABLE addresses (
    id          SERIAL PRIMARY KEY,
    street      VARCHAR(100),
    house_no    VARCHAR(50),
    zip_code    VARCHAR(20),
    city        VARCHAR(100)
);

--  Benutzer-Tabelle
CREATE TABLE users (
    id                SERIAL PRIMARY KEY,
    last_name         VARCHAR(65) NOT NULL,
    first_name        VARCHAR(65) NOT NULL,
    gender            VARCHAR(20),
    birth_date        DATE,
    email             VARCHAR(100) NOT NULL UNIQUE,
    phone             VARCHAR(50),
    created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    address_id        INT REFERENCES addresses(id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,
    interested_in     VARCHAR(20)
);

--  Hobby-Tabelle
CREATE TABLE hobbies (
    id       SERIAL PRIMARY KEY,
    name     VARCHAR(255) NOT NULL UNIQUE
);

--  Benutzer-Hobby (mit Prioritäten)
CREATE TABLE user_hobbies (
    id         SERIAL PRIMARY KEY,
    user_id    INT NOT NULL,
    hobby_id   INT NOT NULL,
    priority   INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (hobby_id) REFERENCES hobbies(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

--  Freundschafts-Tabelle
CREATE TABLE friendships (
    user_1_id INT NOT NULL,
    user_2_id INT NOT NULL,
    status    VARCHAR(50),
    PRIMARY KEY (user_1_id, user_2_id),
    FOREIGN KEY (user_1_id) REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (user_2_id) REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

--  Like-Tabelle (für Matches)
CREATE TABLE likes (
    id            SERIAL PRIMARY KEY,
    user_id       INT NOT NULL,
    liked_user_id INT NOT NULL,
    status        VARCHAR(50),
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (liked_user_id) REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

--  Gesprächs-Tabelle (Conversation)
CREATE TABLE conversations (
    id             SERIAL PRIMARY KEY,
    user_1_email   VARCHAR(255) REFERENCES users(email)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    user_2_email   VARCHAR(255) REFERENCES users(email)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

--  Nachrichten-Tabelle (Messages)
CREATE TABLE messages (
    id               SERIAL PRIMARY KEY,
    conversation_id  INT NOT NULL,
    sender_id        INT NOT NULL,
    receiver_id      INT NOT NULL,
    message_text     TEXT NOT NULL,
    send_time        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (sender_id) REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

--  Benutzer-Fotos (Images)
CREATE TABLE user_photos (
    id          SERIAL PRIMARY KEY,
    user_id     INT NOT NULL,
    photo_data  BYTEA,
    photo_url   VARCHAR(255),
    description VARCHAR(255),
    is_profile  BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

--  Benutzer-Profilbilder (Verknüpfung User <-> Images)
CREATE TABLE user_images (
    image_id  INT REFERENCES user_photos(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    user_id   INT REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    PRIMARY KEY (image_id, user_id)
);

--  TRIGGER für updated_at (statt ON UPDATE CURRENT_TIMESTAMP)
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_timestamp
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_modified_column();
