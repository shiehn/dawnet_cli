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

def set_or_update_token(token=None):
    if token is None:
        token = generate_uuid()
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
    token_actions = ['Set Token', 'Get Token', 'Refresh/Generate Token', 'Go Back']
    selected_action = select(
        "Token management options:",
        choices=token_actions,
    ).ask()

    if selected_action == 'Set Token':
        token = click.prompt("Enter the new token", type=str)
        set_or_update_token(token)
        click.echo(f"Token has been updated to: {token}")
    elif selected_action == 'Get Token':
        token = read_token_from_file()
        if token:
            click.echo(f"Current token: {token}")
        else:
            click.echo("No token found. A token will be generated.")
            set_or_update_token()
    elif selected_action == 'Refresh/Generate Token':
        new_token = set_or_update_token()
        click.echo(f"New token generated: {new_token}")
    elif selected_action == 'Go Back':
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
    cli()
