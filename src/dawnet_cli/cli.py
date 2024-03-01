import click
from questionary import select
from .api import get_remotes


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        base_options(ctx)

def base_options(ctx):
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
    """What would you like to do with the remotes?"""
    remote_options = ['list', 'menu']
    selected_remote_option = select(
        "Select an action:",
        choices=remote_options,
    ).ask()  # .ask() displays the prompt

    if selected_remote_option == 'list':
        for remote in get_remotes():
            click.echo(remote)
    elif selected_remote_option == 'run':
        click.echo("Remote run action not implemented.")
    elif selected_remote_option == 'menu':
        ctx.invoke(cli())
        #pass

if __name__ == '__main__':
    cli()
