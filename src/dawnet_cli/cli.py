import click
from questionary import select
import os
import platform
from .persistence import set_or_update_token, read_token_from_file, generate_uuid
from .api import get_remotes


def clear_screen():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')


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

    clear_screen()

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

    clear_screen()

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
    remote_options = ['list', 'menu']
    selected_remote_option = select(
        "Select an action:",
        choices=remote_options,
    ).ask()

    clear_screen()

    if selected_remote_option == 'list':
        list_categories(ctx)
    elif selected_remote_option == 'menu':
        menu(ctx)


def list_categories(ctx):
    category_options = ['all', 'running', 'available', 'installed', 'menu']
    selected_category = select(
        "Select a category to list:",
        choices=category_options,
    ).ask()

    clear_screen()

    if selected_category:
        if selected_category == 'menu':
            menu(ctx)

        list_remotes(ctx, selected_category)


def list_remotes(ctx, selected_category):
    remotes = get_remotes()

    # Append 'menu' option to the remotes list
    remotes.append('menu')

    selected_remote = select(
        "Select a remote to manage:",
        choices=remotes,
    ).ask()

    clear_screen()

    if selected_remote:
        if selected_remote == 'menu':
            menu(ctx)
        else:
            manage_remote(ctx, selected_remote, selected_category)


def manage_remote(ctx, remote_name, selected_category):
    actions = []
    if selected_category == 'running':
        actions = ['stop', 'menu']
    elif selected_category == 'installed':
        actions = ['run', 'stop', 'menu']
    elif selected_category == 'available':
        actions = ['install', 'menu']
    elif selected_category == 'all':
        actions = ['run', 'stop', 'install', 'menu']

    selected_action = select(
        f"Select an action for {remote_name}:",
        choices=actions,
    ).ask()

    clear_screen()

    if selected_action == 'menu':
        list_categories(ctx)  # Modify to return to the category selection
    else:
        print(f"{selected_action} action for {remote_name} not implemented.")


if __name__ == '__main__':
    clear_screen()
    token = read_token_from_file()

    if token is None:
        print(set_or_update_token(token=generate_uuid()))

    cli()
