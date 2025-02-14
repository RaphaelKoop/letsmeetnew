import pandas as pd
import psycopg2
import re
from datetime import datetime
import xml.etree.ElementTree as ET
from pymongo import MongoClient

## Datenquellen
EXCEL_FILE = "Lets Meet DB Dump.xlsx"
XML_FILE = "Lets_Meet_Hobbies.xml"

## Verbindungseinstellungen
MONGO_URI = "mongodb://localhost:27017"
MONGO_DB = "LetsMeet"
MONGO_COLLECTION = "users"

POSTGRES_HOST = "localhost"
POSTGRES_DB = "lf8_lets_meet_db"
POSTGRES_USER = "user"
POSTGRES_PWD = "secret"
POSTGRES_PORT = 5433  # Falls dein Compose-File "5433:5432" nutzt


def main():
    """ Hauptprogramm für den Datenimport """
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PWD,
            port=POSTGRES_PORT
        )
        conn.set_client_encoding('UTF8')
        cursor = conn.cursor()
        print("✅ Verbindung zur PostgreSQL-Datenbank erfolgreich!")

        # Daten importieren
        import_from_excel(cursor, conn)
        import_from_mongo(cursor, conn)
        import_from_xml(cursor, conn)

        # Verbindung schließen
        cursor.close()
        conn.close()
        print("✅ Alle Daten wurden erfolgreich importiert!")

    except Exception as e:
        print(f"❌ Verbindungsfehler: {e}")


def import_from_excel(cursor, conn):
    """ Importiert Daten aus der Excel-Datei """
    print("🔄 Starte Excel-Import...")

    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=0)

        df.columns = [
            "nachname_vorname",
            "strasse_plz_ort",
            "telefon",
            "hobbies_raw",
            "email",
            "geschlecht",
            "interessiert_an",
            "geburtsdatum"
        ]

        for _, row in df.iterrows():
            first_name, last_name = split_name_simple(row["nachname_vorname"])
            street, house_no, zip_code, city = parse_address(row["strasse_plz_ort"])
            address_id = get_or_create_address(cursor, street, house_no, zip_code, city)

            phone = re.sub(r"[^0-9+]", "", str(row["telefon"])) if pd.notnull(row["telefon"]) else None
            gender = str(row["geschlecht"]) if pd.notnull(row["geschlecht"]) else None
            birth_date = parse_date_ddmmYYYY(str(row["geburtsdatum"]))
            email = str(row["email"]) if pd.notnull(row["email"]) else None
            interested_in = str(row["interessiert_an"]) if pd.notnull(row["interessiert_an"]) else None

            hobbies = extract_hobbies(row["hobbies_raw"])
            user_id = get_or_create_user(cursor, first_name, last_name, phone, email, gender, birth_date, address_id, interested_in)

            if user_id:
                for hobby_name, priority in hobbies:
                    hobby_id = get_or_create_hobby(cursor, hobby_name)
                    cursor.execute(
                        "INSERT INTO user_hobbies (user_id, hobby_id, priority) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                        (user_id, hobby_id, priority)
                    )

        conn.commit()
        print("✅ Excel-Import abgeschlossen!")

    except Exception as e:
        print(f"❌ Fehler beim Excel-Import: {e}")


def get_or_create_address(cursor, street, house_no, zip_code, city):
    """ Erstellt oder findet eine Adresse """
    if not street and not city:
        return None

    cursor.execute("SELECT id FROM addresses WHERE street = %s AND house_no = %s AND zip_code = %s AND city = %s",
                   (street, house_no, zip_code, city))
    row = cursor.fetchone()
    if row:
        return row[0]

    cursor.execute("INSERT INTO addresses (street, house_no, zip_code, city) VALUES (%s, %s, %s, %s) RETURNING id",
                   (street, house_no, zip_code, city))
    return cursor.fetchone()[0]


def get_or_create_user(cursor, first_name, last_name, phone, email, gender, birth_date, address_id, interested_in):
    """ Erstellt oder findet einen Benutzer """
    if not email:
        return None

    cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
    row = cursor.fetchone()
    if row:
        return row[0]

    cursor.execute("""
        INSERT INTO users (first_name, last_name, phone, email, gender, birth_date, address_id, interested_in)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING user_id
    """, (first_name, last_name, phone, email, gender, birth_date, address_id, interested_in))

    return cursor.fetchone()[0]


def get_or_create_hobby(cursor, hobby_name):
    """ Erstellt oder findet ein Hobby """
    cursor.execute("SELECT hobby_id FROM hobbies WHERE name = %s", (hobby_name,))
    row = cursor.fetchone()
    if row:
        return row[0]

    cursor.execute("INSERT INTO hobbies (name) VALUES (%s) RETURNING hobby_id", (hobby_name,))
    return cursor.fetchone()[0]


def split_name_simple(name_str):
    """ Trennt Vorname und Nachname """
    if not name_str:
        return ("-", "-")
    parts = name_str.split(",", 1)
    return (parts[1].strip(), parts[0].strip()) if len(parts) == 2 else ("-", name_str.strip())


def parse_address(addr_str):
    """ Parst Adresse in Straße, Hausnummer, PLZ und Stadt """
    parts = [p.strip() for p in addr_str.split(",")]
    if len(parts) >= 3:
        street, house_no = parts[0].rsplit(" ", 1) if " " in parts[0] else (parts[0], None)
        return street, house_no, parts[1], parts[2]
    return None, None, None, None


def parse_date_ddmmYYYY(date_str):
    """ Parst Datum im Format TT.MM.YYYY """
    try:
        return datetime.strptime(date_str.strip(), "%d.%m.%Y").date()
    except:
        return None


def extract_hobbies(hobby_str):
    """ Parst Hobbys mit Prioritäten """
    hobbies = []
    for h in hobby_str.split(";"):
        match = re.search(r"(.*?)%(\d+)%", h)
        if match:
            hobbies.append((match.group(1).strip(), int(match.group(2))))
        else:
            hobbies.append((h.strip(), 0))
    return hobbies


def import_from_mongo(cursor, conn):
    """ Importiert Daten aus MongoDB """
    print("🔄 Starte MongoDB-Import...")
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client[MONGO_DB]
    collection = db[MONGO_COLLECTION]

    for doc in collection.find({}):
        email = doc.get("_id", "")
        name = doc.get("name", "")
        phone = re.sub(r"[^0-9+]", "", doc.get("phone", "")) if doc.get("phone") else None

        first_name, last_name = split_name_simple(name)
        user_id = get_or_create_user(cursor, first_name, last_name, phone, email, None, None, None, None)

        if user_id:
            for friend_email in doc.get("friends", []):
                friend_id = get_or_create_user(cursor, "-", "-", None, friend_email, None, None, None, None)
                cursor.execute("INSERT INTO friendships (user_id1, user_id2) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                               sorted([user_id, friend_id]))

    conn.commit()
    print("✅ MongoDB-Import abgeschlossen!")


def import_from_xml(cursor, conn):
    """ Importiert Hobbys aus XML """
    print("🔄 Starte XML-Import...")
    tree = ET.parse(XML_FILE)
    root = tree.getroot()

    for hobby in root.findall("hobby"):
        get_or_create_hobby(cursor, hobby.text.strip())

    conn.commit()
    print("✅ XML-Import abgeschlossen!")


if __name__ == "__main__":
    main()
