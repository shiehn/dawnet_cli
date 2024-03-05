import sqlite3
import uuid
import click

from .models import RemoteContainer

# Database setup
db_path = 'docker_containers.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# CONTAINER STATUS ###############################

# Create table for storing container PIDs
# Update the container_pids table schema
cursor.execute('''
CREATE TABLE IF NOT EXISTS container_pids
(id INTEGER PRIMARY KEY,
 pid INTEGER,
 container_id TEXT,
 remote_name TEXT,
 associated_token TEXT,
 status INTEGER)
''')
conn.commit()


# DELETE ME, JUST ADDING A ROW
# Prepare the INSERT INTO statement
# insert_query = '''
# INSERT INTO container_pids (pid, container_id, remote_name, associated_token, status)
# VALUES (?, ?, ?, ?, ?)
# '''
#
# # Values to insert
# # Assuming placeholder values for pid, container_id, and status
# # You should replace these with the actual values you wish to insert
# pid_value = 1  # Example pid value
# container_id_value = "example_container_id"  # Example container ID
# remote_name_value = "Hello Docker"  # The remote_name value you want to insert
# associated_token_value = None
# status_value = 0  # Example status value
#
#
# # Execute the insert query with the values
# cursor.execute(insert_query, (pid_value, container_id_value, remote_name_value, associated_token_value, status_value))
#
# # Commit the changes to the database
# conn.commit()
# # END DELETE ME


# Existing UUID Token Table and Functions...

# Updated save_pid function
def save_container_state(pid, container_id, remote_name, associated_token, status):
    cursor.execute("INSERT INTO container_pids (pid, container_id, remote_name, associated_token, status) VALUES (?, ?, ?, ?, ?)",
                   (pid, container_id, remote_name, associated_token, status))
    conn.commit()
    print(f"associated_token: {associated_token}")


# New update_status function
def update_container_state(container_id, status):
    cursor.execute("UPDATE container_pids SET status = ? WHERE container_id = ?", (status, container_id))
    conn.commit()


def get_container_states(status=None):
    if status is None:
        cursor.execute("SELECT id, pid, container_id, remote_name, associated_token, status FROM container_pids")
    else:
        cursor.execute("SELECT id, pid, container_id, remote_name, associated_token, status FROM container_pids WHERE status = ?",
                       (status,))

    rows = cursor.fetchall()
    containers = [RemoteContainer(*row) for row in rows]
    return containers


# CONNECTION TOKEN ###############################

# Extend the database schema to include a table for the UUID token
cursor.execute('''
CREATE TABLE IF NOT EXISTS uuid_token
(id INTEGER PRIMARY KEY, token TEXT)''')
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
