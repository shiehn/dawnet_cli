import sys

import click
from questionary import select
import os
import platform

from .models import RemoteContainer, RemoteSource
from .containers import docker_check, start_container, stop_container, build_image, format_image_name, \
    is_container_running, tail_logs
from .persistence import set_or_update_token, generate_uuid, read_token_from_db, get_container_states
from .api import get_remote_images, get_remote_sources
from .builder import DockerImageBuilder


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
    option_title = "Welcome to DAWnet!"
    option_tokens = 'tokens (connect your remotes)'
    option_remotes = 'remotes (ready to run)'
    option_sources = 'sources (ready to build)'

    entry_options = [option_tokens, option_remotes, option_sources]
    selected_entry_option = select(
        option_title,
        choices=entry_options,
    ).ask()

    clear_screen()

    if selected_entry_option == option_tokens:
        tokens_menu(ctx)
    elif selected_entry_option == option_remotes:
        list_categories(ctx)
    elif selected_entry_option == option_sources:
        source_menu(ctx)
    else:
        click.echo(f"Error: Unexpected selection: {selected_entry_option}")


def tokens_menu(ctx):
    token_actions = ['view current token', 'add your token', 'generate a new token', 'menu']
    selected_action = select(
        "Token management options:",
        choices=token_actions,
    ).ask()

    clear_screen()

    if selected_action == 'add your token':
        token = click.prompt("Enter the new token", type=str)
        if not set_or_update_token(token):
            menu(ctx)

        click.echo(f"Token has been updated to: {token}")
    elif selected_action == 'view current token':
        token = read_token_from_db()
        if token:
            click.echo(f"CURRENT TOKEN: {token}")
        else:
            click.echo("No token found. A token will be generated.")
            set_or_update_token()
    elif selected_action == 'generate a new token':
        new_token = set_or_update_token()
        click.echo(f"New token generated: {new_token}")
    elif selected_action == 'menu':
        menu(ctx)

    menu(ctx)


def source_menu(ctx):
    title = 'Welcome to DAWnet! (Source Code)'
    option_build = 'build (remotes from source code)'
    option_list = 'list (remote source code)'
    option_menu = 'menu'

    token_actions = [
        option_build,
        option_list,
        option_menu]
    selected_action = select(
        title,
        choices=token_actions,
    ).ask()

    clear_screen()

    if selected_action == option_build:
        # TODO validate the url & name
        source_url = click.prompt("Enter the url of the source code to build", type=str)
        image_name = click.prompt("Enter a name for the docker image to build", type=str)

        # BUILD THE IMAGE
        try:
            builder = DockerImageBuilder()
            builder.build_docker_image(source_url, image_name)
        except Exception as e:
            click.echo(f"Error building the docker image: {e}")
            menu(ctx)
    elif selected_action == option_list:

        remotes = get_remote_sources()

        remotes.append(
            RemoteSource(
                remote_name='menu',
                remote_description='',
                source_url='',
                remote_version=''
            )
        )

        # remotes.append(RemoteContainer(0, 0, 0, "menu", ""))

        selected_remote = select(
            "Manage a remote source:",
            choices=[
                {"name": "menu", "value": container} if container.remote_name == "menu"
                else
                {"name": f"{container.remote_name} - {container.source_url}", "value": container} for
                container in remotes],
        ).ask()

    else:
        menu(ctx)


def list_categories(ctx):
    category_options = ['running', 'available', 'menu']
    selected_category = select(
        "List remotes:",
        choices=category_options,
    ).ask()

    clear_screen()

    if selected_category:
        if selected_category == 'menu':
            menu(ctx)

        list_remotes(ctx, selected_category)


def list_remotes(ctx, selected_category):
    remotes = []

    if selected_category == 'running':
        db_containers = get_container_states(status=1)
        for db_container in db_containers:
            # print(f"CONTAINER: {db_container}")
            if is_container_running(db_container.container_id):
                # print(f"PID: {db_container.pid}")
                # print(f"TOKEN: {db_container.associated_token}")
                remotes.append(db_container)
            else:
                stop_container(db_container.container_id)  # Sync the database with the actual state

        # Append 'menu' option to the remotes list
        remotes.append(RemoteContainer(0, 0, 0, "menu", ""))

        selected_remote = select(
            "Select a running remote:",
            choices=[
                {"name": "menu", "value": container} if container.remote_name == "menu"
                else {
                    "name": f"{container.remote_name} - {container.remote_description} [{container.associated_token}]",
                    "value": container} for
                container in remotes
            ],
        ).ask()
    else:
        remotes = get_remote_images()

        # Append 'menu' option to the remotes list
        remotes.append(RemoteContainer(0, 0, 0, "menu"))

        selected_remote = select(
            "Select a remote to manage:",
            choices=[
                {"name": "menu", "value": container} if container.remote_name == "menu"
                else {"name": f"{container.remote_name} - {container.remote_description}", "value": container}
                for container in remotes
            ],
        ).ask()

    clear_screen()

    if selected_remote:
        if selected_remote.remote_name == 'menu':
            menu(ctx)
        else:
            manage_remote(ctx, selected_remote, selected_category)


def manage_remote(ctx, selected_remote, selected_category):
    actions = []
    if selected_category == 'running':
        actions = ['stop', 'logs', 'menu']
    elif selected_category == 'available':
        actions = ['run', 'menu']

    selected_action = select(
        f"Select an action for {selected_remote.remote_name}:",
        choices=actions,
    ).ask()

    clear_screen()

    # print(f"SELECTED CATEGORY: {selected_action}")

    if selected_action == 'menu':
        list_categories(ctx)  # Modify to return to the category selection
    elif selected_action == 'run':
        # start_container("hello-docker", command=None, name=None)
        start_container(selected_remote.image_name, selected_remote.remote_name, selected_remote.remote_description,
                        read_token_from_db())
    elif selected_action == 'stop':
        # print("F'n STOP")
        stop_container(selected_remote.container_id)
    elif selected_action == 'logs':
        tail_logs(selected_remote.container_id)
    elif selected_action == 'install':
        print("INSTALLL BITCH")
        formatted_name = format_image_name(selected_remote.remote_name)
        img_name = build_image(formatted_name, '/home/stevehiehn/dawnet/dawnet_cli/docker_image')
        print(f"Image build success! Name={img_name}")
    else:
        print(f"{selected_action} action for {selected_remote.remote_name} not implemented.")


if __name__ == '__main__':
    clear_screen()

    success = docker_check()
    if not success:
        click.echo("Error: Unable to connect to Docker.  Please ensure Docker is RUNNING and on the system PATH.")
        sys.exit(1)  # Exit with error code 1 if Docker is not accessible

    token = read_token_from_db()
    if token is None:
        print(set_or_update_token(token=generate_uuid()))

    cli()
