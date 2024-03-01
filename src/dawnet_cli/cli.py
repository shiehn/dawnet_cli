import click
from questionary import select
from .api import get_remotes
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

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        menu(ctx)

def menu(ctx):
    entry_options = ['tokens', 'remotes']
    selected_entry_option = select(
        "Would you like to manage:",
        choices=entry_options,
    ).ask()

    if selected_entry_option == 'tokens':
        tokens_menu(ctx)
    elif selected_entry_option == 'remotes':
        ctx.invoke(remotes)

def tokens_menu(ctx):
    token_actions = ['current token', 'set token', 'generate new token', 'menu']
    selected_action = select(
        "Token management options:",
        choices=token_actions,
    ).ask()

    if selected_action == 'set token':
        token = click.prompt("Enter the new token", type=str)
        if not set_or_update_token(token):
            menu(ctx)

        click.echo(f"Token has been updated to: {token}")
    elif selected_action == 'current token':
        token = read_token_from_file()
        if token:
            click.echo(f"current token: {token}")
        else:
            click.echo("No token found. A token will be generated.")
            set_or_update_token()
    elif selected_action == 'generate new token':
        new_token = set_or_update_token()
        click.echo(f"New token generated: {new_token}")
    elif selected_action == 'menu':
        menu(ctx)

    menu(ctx)

@cli.command()
@click.pass_context
def remotes(ctx):
    remote_options = ['list', 'Go Back']
    selected_remote_option = select(
        "Select an action:",
        choices=remote_options,
    ).ask()

    if selected_remote_option == 'list':
        list_categories(ctx)
    elif selected_remote_option == 'Go Back':
        print("Going back to the main menu...")

def list_categories(ctx):
    category_options = ['available', 'installed', 'running', 'all']
    selected_category = select(
        "Select a category to list:",
        choices=category_options,
    ).ask()

    if selected_category:
        list_remotes(ctx, selected_category)

def list_remotes(ctx, category):
    # Placeholder: Replace with actual logic to fetch remotes based on category
    # For demonstration, we'll just call get_remotes regardless of the category
    remotes = get_remotes()
    selected_remote = select(
        "Select a remote to manage:",
        choices=remotes,
    ).ask()

    if selected_remote:
        manage_remote(ctx, selected_remote)

def manage_remote(ctx, remote_name):
    actions = ['run', 'stop', 'install', 'Go Back']
    selected_action = select(
        f"Select an action for {remote_name}:",
        choices=actions,
    ).ask()

    if selected_action == 'Go Back':
        list_categories(ctx)  # Modify to return to the category selection
    else:
        print(f"{selected_action} action for {remote_name} not implemented.")

if __name__ == '__main__':
    token = read_token_from_file()

    if token is None:
        print(set_or_update_token(token=generate_uuid()))

    cli()
