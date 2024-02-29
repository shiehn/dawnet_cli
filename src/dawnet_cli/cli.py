import click
from questionary import select
from .api import get_remotes

@click.group()
def cli():
    """DAWnet Command Line Interface."""
    pass

def list_remotes():
    for remote in get_remotes():
        print(remote)

@cli.command()
def remotes():
    """Manage DAWnet Remotes."""
    remote_options = ['list', 'run']
    # Use questionary to let the user select a remote from the list
    selected_remote = select(
        "Select a action:",
        choices=remote_options,
    ).ask()  # .ask() displays the prompt

    if selected_remote == 'list':  # If a selection was made
        list_remotes()
    elif selected_remote == 'run':
        """Manage DAWnet Remotes."""
        remote_list = get_remotes()
        # Use questionary to let the user select a remote from the list
        selected_remote = select(
            "Select a remote:",
            choices=remote_list,
        ).ask()  # .ask() displays the prompt

        if selected_remote:  # If a selection was made
            print(f"You selected: {selected_remote}")
        else:
            print("No selection was made.")

@cli.command()
def greet():
    """Display the welcome message."""
    print('Welcome to the DAWnet CLI!')

if __name__ == '__main__':
    cli()
