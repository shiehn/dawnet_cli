import sqlite3
import uuid
import click

# Database setup
db_path = 'docker_containers.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create table for storing container PIDs
cursor.execute('''
CREATE TABLE IF NOT EXISTS container_pids
(container_id TEXT PRIMARY KEY, pid INTEGER)''')

# Extend the database schema to include a table for the UUID token
cursor.execute('''
CREATE TABLE IF NOT EXISTS uuid_token
(id INTEGER PRIMARY KEY, token TEXT)''')
conn.commit()


def save_pid(container_id, pid):
    cursor.execute("INSERT INTO container_pids (container_id, pid) VALUES (?, ?)",
                   (container_id, pid))
    conn.commit()


def delete_pid(container_id):
    cursor.execute("DELETE FROM container_pids WHERE container_id = ?", (container_id,))
    conn.commit()


def generate_uuid():
    return str(uuid.uuid4())


def save_token_to_db(token):
    # Clear the existing token before saving the new one
    cursor.execute("DELETE FROM uuid_token")
    # Insert the new token
    cursor.execute("INSERT INTO uuid_token (token) VALUES (?)", (token,))
    conn.commit()


def read_token_from_db():
    cursor.execute("SELECT token FROM uuid_token LIMIT 1")
    row = cursor.fetchone()
    return row[0] if row else None


def is_valid_uuid(uuid_to_test, version=4):
    try:
        uuid_obj = uuid.UUID(uuid_to_test, version=version)
        return str(uuid_obj) == uuid_to_test and uuid_obj.version == version
    except ValueError:
        return False


def set_or_update_token(token=None):
    if token is None:
        token = generate_uuid()

    if not is_valid_uuid(token):
        click.echo(f"Token: {token}, is not a valid UUID.")
        return None

    save_token_to_db(token)
    return token
