import click
from questionary import select
from .api import get_remotes


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        menu(ctx)

def menu(ctx):
    """Prompt user for base options if no command is provided."""
    entry_options = ['tokens', 'remotes']
    selected_entry_option = select(
        "Would you like to manage:",
        choices=entry_options,
    ).ask()  # .ask() displays the prompt

    # Directly invoke the corresponding command based on the user's selection
    if selected_entry_option == 'tokens':
        ctx.invoke(tokens)
    elif selected_entry_option == 'remotes':
        ctx.invoke(remotes)

@cli.command()
def tokens():
    """Manage DAWnet Tokens."""
    click.echo("Token management not implemented.")

@cli.command()
@click.pass_context
def remotes(ctx):
    """Manage DAWnet Remotes."""
    remote_options = ['list', 'Go Back']
    selected_remote_option = select(
        "Select an action:",
        choices=remote_options,
    ).ask()

    if selected_remote_option == 'list':
        list_remotes(ctx)
    elif selected_remote_option == 'Go Back':
        # Optionally, implement a way to go back to the previous menu or main menu
        print("Going back to the main menu...")

def list_remotes(ctx):
    remotes = get_remotes()
    selected_remote = select(
        "Select a remote to manage:",
        choices=remotes,
    ).ask()

    if selected_remote:
        manage_remote(ctx, selected_remote)

def manage_remote(ctx, remote_name):
    """Present options for managing a selected remote."""
    actions = ['run', 'stop', 'install', 'Go Back']
    selected_action = select(
        f"Select an action for {remote_name}:",
        choices=actions,
    ).ask()

    if selected_action == 'Go Back':
        list_remotes(ctx)  # Return to the list of remotes
    else:
        # Here, you'd implement the logic for running, stopping, or installing based on the remote
        print(f"{selected_action} action for {remote_name} not implemented.")

if __name__ == '__main__':
    cli()
