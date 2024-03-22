import sqlite3
import uuid
import click
import os
from appdirs import user_data_dir
from .models import RemoteContainer

# Database setup
# Name of your application
appname = "runes_cli"
appauthor = "Steve Hiehn"

# Determine platform-specific user data directory
data_dir = user_data_dir(appname, appauthor)

# Ensure the directory exists
os.makedirs(data_dir, exist_ok=True)

# Path to the SQLite database within the data directory
db_path = os.path.join(data_dir, "runes_cli.db")

# Connect to the SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# CONTAINER STATUS ###############################

# Create table for storing container PIDs
# Update the container_pids table schema
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS container_pids
(id INTEGER PRIMARY KEY,
 pid INTEGER,
 container_id TEXT,
 remote_name TEXT,
 remote_description TEXT,
 associated_token TEXT,
 status INTEGER)
"""
)
conn.commit()

# Create table for storing Docker Hub credentials
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS docker_hub_credentials
(id INTEGER PRIMARY KEY, username TEXT, encrypted_password TEXT)
"""
)
conn.commit()

from cryptography.fernet import Fernet


def get_fernet_key():
    key_file = os.path.join(data_dir, "fernet.key")
    if os.path.exists(key_file):
        with open(key_file, "rb") as file:
            key = file.read()
    else:
        key = Fernet.generate_key()
        with open(key_file, "wb") as file:
            file.write(key)
    return key


# Generate or load the Fernet key
key = get_fernet_key()
cipher_suite = Fernet(key)


def save_docker_credentials(username, password):
    # Ideally, encrypt the password here
    encrypted_password = cipher_suite.encrypt(password.encode())
    # Clear the existing credentials before saving the new ones
    cursor.execute("DELETE FROM docker_hub_credentials")
    cursor.execute("INSERT INTO docker_hub_credentials (username, encrypted_password) VALUES (?, ?)",
                   (username, encrypted_password))
    conn.commit()


def get_docker_credentials():
    cursor.execute("SELECT username, encrypted_password FROM docker_hub_credentials LIMIT 1")
    row = cursor.fetchone()
    if row:
        username, encrypted_password = row
        # Decrypt the password here
        password = cipher_suite.decrypt(encrypted_password).decode()
        return username, password
    return None, None


# Updated save_pid function
def save_container_state(
        pid, container_id, remote_name, remote_description, associated_token, status
):
    cursor.execute(
        "INSERT INTO container_pids (pid, container_id, remote_name, remote_description, associated_token, status) VALUES (?, ?, ?, ?, ?, ?)",
        (pid, container_id, remote_name, remote_description, associated_token, status),
    )
    conn.commit()
    # print(f"associated_token: {associated_token}")


# New update_status function
def update_container_state(container_id, status):
    cursor.execute(
        "UPDATE container_pids SET status = ? WHERE container_id = ?",
        (status, container_id),
    )
    conn.commit()


def get_container_states(status=None):
    if status is None:
        cursor.execute(
            "SELECT id, pid, container_id, remote_name, remote_description, associated_token, status FROM container_pids"
        )
    else:
        cursor.execute(
            "SELECT id, pid, container_id, remote_name, remote_description, associated_token, status FROM container_pids WHERE status = ?",
            (status,),
        )

    rows = cursor.fetchall()
    containers = [RemoteContainer(*row) for row in rows]
    return containers


# CONNECTION TOKEN ###############################

# Extend the database schema to include a table for the UUID token
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS uuid_token
(id INTEGER PRIMARY KEY, token TEXT)"""
)
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
