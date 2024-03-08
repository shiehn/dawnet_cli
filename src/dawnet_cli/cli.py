import sys
import click
import docker
from questionary import select
import os
import re
import platform
from urllib.parse import urlparse

from .models import RemoteContainer, RemoteSource
from .containers import (
    docker_check,
    start_container,
    stop_container,
    is_container_running,
    tail_logs,
)
from .persistence import (
    set_or_update_token,
    generate_uuid,
    read_token_from_db,
    get_container_states,
)
from .api import get_remote_images, get_remote_sources
from .builder import DockerImageBuilder


def clear_screen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        menu(ctx)


def menu(ctx):
    option_title = "Welcome to DAWnet!"
    option_tokens = "tokens (connect your remotes)"
    option_remotes = "remotes (ready to run)"
    option_sources = "sources (ready to build)"
    option_docker = "docker-images (publish or run)"

    entry_options = [option_tokens, option_remotes, option_sources, option_docker]
    selected_entry_option = select(
        option_title,
        choices=entry_options,
    ).ask()

    clear_screen()

    if selected_entry_option == option_tokens:
        tokens_menu(ctx)
    elif selected_entry_option == option_remotes:
        remote_menu(ctx)
    elif selected_entry_option == option_docker:
        docker_menu(ctx)
    elif selected_entry_option == option_sources:
        source_menu(ctx)
    else:
        click.echo(f"Error: Unexpected selection: {selected_entry_option}")


def tokens_menu(ctx):
    token_actions = [
        "view current token",
        "add your token",
        "generate a new token",
        "menu",
    ]
    selected_action = select(
        "Token management options:",
        choices=token_actions,
    ).ask()

    clear_screen()

    if selected_action == "add your token":
        token = click.prompt("Enter the new token", type=str)
        if not set_or_update_token(token):
            menu(ctx)

        click.echo(f"Token has been updated to: {token}")
    elif selected_action == "view current token":
        token = read_token_from_db()
        if token:
            click.echo(f"CURRENT TOKEN: {token}")
        else:
            click.echo("No token found. A token will be generated.")
            set_or_update_token()
    elif selected_action == "generate a new token":
        new_token = set_or_update_token()
        click.echo(f"New token generated: {new_token}")
    elif selected_action == "menu":
        menu(ctx)

    menu(ctx)


# options
option_menu = "menu"

# source options
option_source_build = "build (remotes from source code)"
option_source_list = "list (remote source code)"

# remote options
option_remote_running = "running (active remotes)"
option_remote_available = "available (to run remotes)"

# docker options
option_docker_run_cpu = "run (a cpu docker-image as a dawnet remote)"
option_docker_run_gpu = "run (a gpu docker-image as a dawnet remote)"
option_docker_publish = "publish (a docker-image as a dawnet remote)"


def is_valid_docker_image_name(name):
    """
    Check if the given name is a valid Docker image name.
    """
    # Docker image names must be lowercase and match the following regex for the part after the last '/' (if any)
    return bool(re.match(r"^[a-z0-9._-]+$", name.split("/")[-1]))


def validate_docker_image_name(name):
    """Check if the Docker image name is valid."""
    if not re.match("^[a-z0-9._/-]+$", name):
        return False
    return True


def validate_notebook_source(source):
    """Check if the notebook source is a valid URL or an existing local file."""
    # Check if source is a URL
    if urlparse(source).scheme in ["http", "https"]:
        # Here, we're not performing a deep validation of the URL (e.g., by making a request to it)
        # because this could introduce unnecessary complexity and delays.
        # Basic scheme check is performed to ensure it's a URL.
        return True
    else:
        # Check if source is a local file path and it exists
        if source.endswith(".ipynb") and os.path.isfile(source):
            return True
        else:
            return False


def source_menu(ctx):
    title = "Welcome to DAWnet! (Source Code)"

    token_actions = [option_source_build, option_source_list, option_menu]
    selected_action = select(
        title,
        choices=token_actions,
    ).ask()

    clear_screen()

    if selected_action == option_source_build:
        source_url = click.prompt(
            "Enter a url or path to a `.ipynb` file to build", type=str
        )
        image_name = get_valid_docker_image_name()

        # BUILD THE IMAGE
        try:
            builder = DockerImageBuilder()
            builder.build_docker_image(source_url, image_name)
        except Exception as e:
            click.echo(f"Error building the docker image: {e}")
            menu(ctx)
    elif selected_action == option_source_list:
        remotes = get_remote_sources()

        remotes.append(
            RemoteSource(
                remote_name=option_menu,
                remote_description="",
                source_url="",
                remote_version="",
            )
        )

        # remotes.append(RemoteContainer(0, 0, 0, "menu", ""))

        selected_source = select(
            "Build an image from source code:",
            choices=[
                {"name": "menu", "value": container}
                if container.remote_name == "menu"
                else {
                    "name": f"{container.remote_name} - {container.source_url}",
                    "value": container,
                }
                for container in remotes
            ],
        ).ask()

        if selected_source.remote_name == "menu":
            clear_screen()
            menu(ctx)

        image_name = click.prompt("Name the docker image you are building", type=str)

        # BUILD THE IMAGE
        try:
            builder = DockerImageBuilder()
            builder.build_docker_image(selected_source.source_url, image_name)
            click.echo(f"Image build success! Image Name = {image_name}")
        except Exception as e:
            click.echo(f"Error building the docker image: {e}")
            menu(ctx)

    else:
        menu(ctx)


def remote_menu(ctx):
    title = "List remotes"
    option_menu = "menu"

    category_options = [option_remote_running, option_remote_available, "menu"]
    selected_category = select(
        title,
        choices=category_options,
    ).ask()

    clear_screen()

    if selected_category:
        if selected_category == option_menu:
            menu(ctx)

        list_remotes(ctx, selected_category)


def docker_menu(ctx):
    title = "Docker image actions"
    category_options = [option_docker_run_cpu, option_docker_publish, option_menu]
    selected_category = select(
        title,
        choices=category_options,
    ).ask()

    clear_screen()

    if selected_category == option_menu:
        menu(ctx)
    else:
        list_docker_images(ctx, selected_category)


def list_docker_images(ctx, selected_action):
    remotes = []

    if (
        selected_action == option_docker_run_cpu
        or selected_action == option_docker_run_gpu
    ):
        client = docker.from_env()
        images = client.images.list()
        # Extract the tags of the images, but only include images with tags
        image_tags = [tag for image in images if image.tags for tag in image.tags]
        for image in image_tags:
            remotes.append(RemoteContainer(0, 0, 0, image, ""))

        # Append 'menu' option to the remotes list
        remotes.append(RemoteContainer(0, 0, 0, "menu", ""))

        selected_docker_image = select(
            "Select a local docker image to run as a remote",
            choices=[
                {"name": option_menu, "value": container}
                if container.remote_name == option_menu
                else {
                    "name": f"{container.remote_name} - {container.remote_description} [{container.associated_token}]",
                    "value": container,
                }
                for container in remotes
            ],
        ).ask()

        clear_screen()

        if selected_docker_image.remote_name == option_menu:
            menu(ctx)
        else:
            use_gpu = True if selected_action == option_docker_run_gpu else False

            start_container(
                selected_docker_image.remote_name,
                selected_docker_image.remote_name,
                selected_docker_image.remote_description,
                read_token_from_db(),
                use_gpu,
            )

    elif selected_action == option_docker_publish:
        click.echo("PUBLISH is currently in development. Check back soon.")
        menu(ctx)
    else:
        menu(ctx)


def list_remotes(ctx, selected_category):
    remotes = []

    if selected_category == option_remote_running:
        db_containers = get_container_states(status=1)
        for db_container in db_containers:
            # print(f"CONTAINER: {db_container}")
            if is_container_running(db_container.container_id):
                # print(f"PID: {db_container.pid}")
                # print(f"TOKEN: {db_container.associated_token}")
                remotes.append(db_container)
            else:
                stop_container(
                    db_container.container_id
                )  # Sync the database with the actual state

        # Append 'menu' option to the remotes list
        remotes.append(RemoteContainer(0, 0, 0, option_menu, ""))

        selected_remote = select(
            "Select a running remote:",
            choices=[
                {"name": option_menu, "value": container}
                if container.remote_name == option_menu
                else {
                    "name": f"{container.remote_name} - {container.remote_description} [{container.associated_token}]",
                    "value": container,
                }
                for container in remotes
            ],
        ).ask()
    else:
        remotes = get_remote_images()

        # Append 'menu' option to the remotes list
        remotes.append(RemoteContainer(0, 0, 0, option_menu))

        selected_remote = select(
            "Select a remote to manage:",
            choices=[
                {"name": option_menu, "value": container}
                if container.remote_name == option_menu
                else {
                    "name": f"{container.remote_name} - {container.remote_description}",
                    "value": container,
                }
                for container in remotes
            ],
        ).ask()

    clear_screen()

    if selected_remote:
        if selected_remote.remote_name == option_menu:
            menu(ctx)
        else:
            manage_remote(ctx, selected_remote, selected_category)


def manage_remote(ctx, selected_remote, selected_category):
    action_run_cpu = "run (with cpu)"
    action_run_gpu = "run (with gpu)"
    action_logs = "logs (display the remote logs)"
    action_stop = "stop (the running remote)"
    action_menu = "menu"

    print(
        f"MANAGE REMOTE: selected_category={selected_category} selected_remote={selected_remote.remote_name}"
    )

    actions = []
    if selected_category == option_remote_running:
        actions = [action_stop, action_logs, action_menu]
    elif selected_category == option_remote_available:
        actions = [action_run_cpu, action_run_gpu, action_menu]

    selected_action = select(
        f"Select an action for {selected_remote.remote_name}:",
        choices=actions,
    ).ask()

    clear_screen()

    if selected_action == option_menu:
        remote_menu(ctx)  # Modify to return to the category selection
    elif selected_action == action_run_cpu or selected_action == action_run_gpu:
        use_gpu = True if selected_action == action_run_gpu else False

        start_container(
            selected_remote.image_name,
            selected_remote.remote_name,
            selected_remote.remote_description,
            read_token_from_db(),
            use_gpu,
        )
        menu(ctx)
    elif selected_action == action_stop:
        # print("F'n STOP")
        stop_container(selected_remote.container_id)
        menu(ctx)
    elif selected_action == action_logs:
        tail_logs(selected_remote.container_id)
        menu(ctx)
    # elif selected_action == 'install':
    #     print("INSTALLL BITCH")
    #     formatted_name = format_image_name(selected_remote.remote_name)
    #     img_name = build_image(formatted_name, '/home/stevehiehn/dawnet/dawnet_cli/docker_image')
    #     print(f"Image build success! Name={img_name}")
    else:
        print(
            f"{selected_action} action for {selected_remote.remote_name} not implemented."
        )


if __name__ == "__main__":
    clear_screen()

    success = docker_check()
    if not success:
        click.echo(
            "Error: Unable to connect to Docker.  Please ensure Docker is RUNNING and on the system PATH."
        )
        sys.exit(1)  # Exit with error code 1 if Docker is not accessible

    token = read_token_from_db()
    if token is None:
        print(set_or_update_token(token=generate_uuid()))

    cli()
