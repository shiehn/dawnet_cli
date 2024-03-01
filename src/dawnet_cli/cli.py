import click
from questionary import select
from .api import get_remotes

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
        ctx.invoke(tokens)
    elif selected_entry_option == 'remotes':
        ctx.invoke(remotes)

@cli.command()
def tokens():
    click.echo("Token management not implemented.")

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
