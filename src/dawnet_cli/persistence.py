import click
import uuid
import json
import os

TOKEN_FILE_PATH = "uuid_token.json"


def generate_uuid():
    return str(uuid.uuid4())


def save_token_to_file(token):
    with open(TOKEN_FILE_PATH, 'w') as f:
        json.dump({"uuid": token}, f)


def read_token_from_file():
    if os.path.exists(TOKEN_FILE_PATH):
        with open(TOKEN_FILE_PATH) as f:
            data = json.load(f)
            return data.get("uuid")
    else:
        return None


def is_valid_uuid(uuid_to_test, version=4):
    """
    Check if uuid_to_test is a valid UUID.

    Parameters:
    uuid_to_test (str): String to test for UUID.
    version (int): UUID version (1, 3, 4, 5). Default is 4.

    Returns:
    bool: True if uuid_to_test is a valid UUID, otherwise False.
    """
    try:
        uuid_obj = uuid.UUID(uuid_to_test, version=version)
        # Check if it's a valid UUID and if it's the same version
        return str(uuid_obj) == uuid_to_test and uuid_obj.version == version
    except ValueError:
        return False


def set_or_update_token(token=None):
    if token is None:
        token = generate_uuid()

    if not is_valid_uuid(token):
        click.echo(f"Token: {token}, is not a valid UUID.")
        return None

    save_token_to_file(token)
    return token
