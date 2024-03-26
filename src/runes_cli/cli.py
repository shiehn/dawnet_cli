import asyncio
import sys
import click
import docker
import requests
import questionary
from questionary import select, prompt
import os
import re
import platform
from urllib.parse import urlparse
import docker
import getpass

from .file_uploader import FileUploader

from .models import RemoteContainer, RemoteSource
from .containers import (
    docker_check,
    start_container,
    stop_container,
    is_container_running,
    tail_logs,
    get_docker_namespace,
)
from .persistence import (
    set_or_update_token,
    generate_uuid,
    read_token_from_db,
    get_container_states,
    get_docker_credentials,
    save_docker_credentials,
)
from .api import (
    get_remote_images,
    get_remote_sources,
    insert_remote_image_info,
    publish_remote_source,
)
from .builder import DockerImageBuilder

# default
default_title = "Welcome to Signals & Sorcery!"

# options
option_menu = "menu"

# source options
option_source_build = "build (elixirs from source code)"
option_source_list = "list (elixir source code)"
option_publish = "publish (elixir source code to the vault)"

# remote options
option_remote_running = "running (active elixirs)"
option_remote_available = "available (to run elixirs)"

# docker options
option_docker_run_cpu = "run (a cpu docker-image as an elixir)"
option_docker_run_gpu = "run (a gpu docker-image as an elixir)"
option_docker_publish = "publish (a docker-image as an elixir)"


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
    option_title = default_title
    option_tokens = "tokens (connect your elixirs)"
    option_remotes = "elixirs (ready to run)"
    option_sources = "elixir source (ready to build)"
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


def get_valid_docker_image_name():
    while True:
        image_name = click.prompt("Enter the Docker image name", type=str)
        if is_valid_docker_image_name(image_name):
            try:
                validate_docker_image_name(image_name)
                return image_name
            except Exception as e:
                click.echo(f"Invalid image name: {e}")
        else:
            click.echo("The provided image name is not valid. Please try again.")


def publish_elixir_source(ctx):
    """
    CLI tool to collect information and publish an Elixir source.
    """

    uploader = FileUploader()
    # uploader.upload(source_url)

    input_source = questionary.text(
        "Enter a local path to an `.ipynb` file or a url to a public Google CoLab:",
        validate=lambda text: 1 <= len(text) <= 1500,
    ).ask()

    if input_source.endswith(".ipynb") and os.path.isfile(input_source):
        # do the file upload stuff and get the source_url from the file uploader
        source_url = asyncio.run(uploader.upload(input_source))
        colab_url = None
    elif urlparse(input_source).scheme in ["http", "https"]:
        source_url = None
        colab_url = input_source
    else:
        click.echo("Invalid Input")
        menu(ctx)

    # Collecting information using questionary
    remote_name = questionary.text(
        "Elixir name (maxLength: 100):",
        validate=lambda text: 1 <= len(text) <= 100,
    ).ask()
    remote_description = questionary.text(
        "Elixir description (maxLength: 250):",
        validate=lambda text: 1 <= len(text) <= 250,
    ).ask()
    remote_category = questionary.text(
        "Elixir category (maxLength: 100):",
        validate=lambda text: 1 <= len(text) <= 100,
    ).ask()
    remote_author = questionary.text(
        "Authors Name (maxLength: 100):",
        validate=lambda text: 1 <= len(text) <= 100,
    ).ask()
    remote_version = questionary.text(
        "Enter remote version (optional, maxLength: 25):",
        validate=lambda text: len(text) <= 25,
    ).ask()

    # Constructing the data dictionary
    data = {
        "remote_name": remote_name,
        "remote_description": remote_description,
        "remote_category": remote_category,
        "remote_author": remote_author,
        "source_url": source_url,
        "colab_url": colab_url if colab_url else None,
        "remote_version": remote_version if remote_version else None,
    }

    response = publish_remote_source(
        remote_name,
        remote_description,
        remote_category,
        remote_author,
        source_url,
        colab_url,
        remote_version,
    )

    # Handling the response
    if response.status_code == 200 or response.status_code == 201:
        click.echo("Elixir source published successfully.")
    else:
        click.echo(
            f"Failed to publish Elixir source. Status code: {response.status_code}"
        )


def source_menu(ctx):
    title = default_title

    token_actions = [
        option_source_build,
        option_source_list,
        option_publish,
        option_menu,
    ]
    selected_action = select(
        title,
        choices=token_actions,
    ).ask()

    clear_screen()

    if selected_action == option_source_build:
        source_url = click.prompt(
            "Enter a URL or path to a `.ipynb` file to build", type=str
        )

        # Check if the source URL is valid
        try:
            validate_notebook_source(source_url)
            image_name = get_valid_docker_image_name()

            # BUILD THE IMAGE
            try:
                builder = DockerImageBuilder()
                builder.build_docker_image(source_url, image_name)
            except Exception as e:
                click.echo(f"Error building the docker image: {e}")
        except Exception as e:
            click.echo(f"Invalid source URL: {e}")

        menu(ctx)
    elif selected_action == option_publish:

        publish_elixir_source(ctx)
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

        selected_source = select(
            "Build an image from source code:",
            choices=[
                (
                    {"name": "menu", "value": container}
                    if container.remote_name == "menu"
                    else {
                        "name": f"{container.remote_name} - {container.source_url} [{container.remote_version}]",
                        "value": container,
                    }
                )
                for container in remotes
            ],
        ).ask()

        if selected_source.remote_name == "menu":
            clear_screen()
            menu(ctx)

        # Check if the source URL is valid
        try:
            validate_notebook_source(selected_source.source_url)
            image_name = get_valid_docker_image_name()

            # BUILD THE IMAGE
            try:
                builder = DockerImageBuilder()
                builder.build_docker_image(selected_source.source_url, image_name)
                clear_screen()
                click.echo(f"Image build success! Image Name = {image_name}")
            except Exception as e:
                click.echo(f"Error building the docker image: {e}")
        except Exception as e:
            click.echo(f"Invalid source URL: {e}")

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

    print("selected_category" + selected_category)

    if selected_category == option_menu:
        menu(ctx)
    else:
        list_docker_images(ctx, selected_category)


def gather_image_info(image_name):
    """
    Prompts the user for missing image information and returns a dictionary with all data.
    """
    questions = [
        {
            "type": "input",
            "name": "remote_name",
            "message": "Name the Elixir:",
            "default": "Default",
        },
        {
            "type": "input",
            "name": "remote_description",
            "message": "Describe the Elixir:",
            "default": "Default",
        },
        {
            "type": "input",
            "name": "remote_category",
            "message": "Categorize the Elixir:",
            "default": "audio",
        },
        {
            "type": "input",
            "name": "remote_author",
            "message": "Authors name:",
            "default": "Default",
        },
        {
            "type": "input",
            "name": "remote_version",
            "message": 'Enter the remote version (default "v0"):',
            "default": "v0",
        },
    ]

    answers = prompt(questions)
    answers["image_name"] = image_name  # Assuming image_name is always provided

    return answers


def list_docker_images(ctx, selected_action):
    remotes = []

    if (
        selected_action == option_docker_run_cpu
        or selected_action == option_docker_run_gpu
        or selected_action == option_docker_publish
    ):
        client = docker.from_env()
        images = client.images.list()
        # Extract the tags of the images, but only include images with tags
        image_tags = [tag for image in images if image.tags for tag in image.tags]
        for image in image_tags:
            remotes.append(RemoteContainer(0, 0, 0, image, ""))

        # Append 'menu' option to the remotes list
        remotes.append(RemoteContainer(0, 0, 0, "menu", ""))

        question = (
            "Select a local docker image to publish to the Elixir Vault"
            if selected_action == option_docker_publish
            else "Select a local docker image to run as an Elixir"
        )

        selected_docker_image = select(
            question,
            choices=[
                (
                    {"name": option_menu, "value": container}
                    if container.remote_name == option_menu
                    else {
                        "name": f"{container.remote_name} - {container.remote_description} [{container.associated_token}]",
                        "value": container,
                    }
                )
                for container in remotes
            ],
        ).ask()

        clear_screen()

        if selected_docker_image.remote_name == option_menu:
            menu(ctx)
            return

        if (
            selected_action == option_docker_run_cpu
            or selected_action == option_docker_run_gpu
        ):

            use_gpu = True if selected_action == option_docker_run_gpu else False

            start_container(
                selected_docker_image.remote_name,
                selected_docker_image.remote_name,
                selected_docker_image.remote_description,
                read_token_from_db(),
                use_gpu,
            )

            menu(ctx)
        elif selected_action == option_docker_publish:
            if check_and_login_to_docker():
                if publish_docker_image(selected_docker_image.remote_name, "latest"):
                    clear_screen()
                    print("Image published to DockerHub successfully.")
                    # Gather missing information
                    username, _ = get_docker_credentials()
                    dockerhub_namespace = get_docker_namespace(username)
                    image_name_with_tag = (
                        f"{dockerhub_namespace}/{selected_docker_image.remote_name}"
                    )
                    image_name = image_name_with_tag.split(":")[0]
                    image_info = gather_image_info(image_name)

                    if insert_remote_image_info(image_info):
                        print("Image information successfully registered.")
                    else:
                        print("Failed to register image information.")

                    return
                else:
                    print("Docker image publish failed.")
                return
            else:
                print("DID NOT SUCCESSFULLY LOGIN TO DOCKER HUB")
                return

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
                (
                    {"name": option_menu, "value": container}
                    if container.remote_name == option_menu
                    else {
                        "name": f"{container.remote_name} - {container.remote_description} [{container.associated_token}]",
                        "value": container,
                    }
                )
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
                (
                    {"name": option_menu, "value": container}
                    if container.remote_name == option_menu
                    else {
                        "name": f"{container.remote_name} - {container.remote_description}",
                        "value": container,
                    }
                )
                for container in remotes
            ],
        ).ask()

    clear_screen()

    if selected_remote:
        if selected_remote.remote_name == option_menu:
            menu(ctx)
        else:
            manage_remote(ctx, selected_remote, selected_category)


def login_to_docker_hub(username, password):
    client = docker.from_env()
    try:
        login_response = client.login(
            username=username, password=password, registry="https://index.docker.io/v1/"
        )
        if login_response.get("Status") == "Login Succeeded":
            print("Logged in to Docker Hub successfully.")
            return True
        else:
            print("Failed to log in to Docker Hub.")
            return False
    except docker.errors.APIError as e:
        print(f"An error occurred while trying to log in to Docker Hub: {e}")
        return False


def check_and_login_to_docker():
    username, password = get_docker_credentials()
    if username and password:
        if login_to_docker_hub(username, password):
            print("Logged in using cached credentials.")
            return True
        else:
            print(f"Failed to log in using cached credentials.{username} {password}")
            return False
    # If no credentials were found or login failed, prompt the user
    username = input("Enter your Docker Hub username: ")
    password = getpass.getpass("Enter your Docker Hub password: ")
    if login_to_docker_hub(username, password):
        # Cache the credentials upon successful login
        save_docker_credentials(username, password)
        return True

    return False


def publish_docker_image(image_name, tag):
    if not check_and_login_to_docker():
        print("Cannot publish the image without logging in.")
        return False

    username, _ = get_docker_credentials()

    dockerhub_namespace = get_docker_namespace(username)

    client = docker.from_env()
    repository_name = (
        f"{dockerhub_namespace}/{image_name}"  # Use the Docker Hub username
    )

    try:
        # Tag the image for the repository
        image = client.images.get(image_name)
        image.tag(repository_name, tag=tag)

        # Initialize variables to track push success and presence of error
        push_success = False
        push_error = False

        # Push the image
        for line in client.images.push(
            repository_name, tag=tag, stream=True, decode=True
        ):
            # Print detailed message if available
            if "status" in line:
                print(line["status"], end="")
                if "progress" in line:
                    print(" " + line["progress"], end="")
                print()  # Newline for next status
                if "digest" in line.get("status", ""):
                    push_success = True  # Digest in status indicates success
            elif "error" in line:
                print(f"Error: {line['error']}")
                push_error = True
                break  # Stop on error

        # Determine the outcome based on presence of error or success
        if push_error:
            print("Docker image publish failed due to an error.")
            return False
        elif push_success:
            print("Image published successfully.")
            return True
        else:
            print(
                "Image push did not complete successfully. Docker image publish failed."
            )
            return False
    except Exception as e:
        print(f"An error occurred while trying to publish the Docker image: {e}")
        return False


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
    #     img_name = build_image(formatted_name, '/home/stevehiehn/dawnet/runes_cli/docker_image')
    #     print(f"Image build success! Name={img_name}")
    else:
        print(
            f"{selected_action} action for {selected_remote.remote_name} not implemented."
        )


def main():
    clear_screen()

    success = docker_check()
    if not success:
        click.echo(
            "Error: Unable to connect to Docker. Please ensure Docker is RUNNING and on the system PATH."
        )
        sys.exit(1)  # Exit with error code 1 if Docker is not accessible

    token = read_token_from_db()
    if token is None:
        print(set_or_update_token(token=generate_uuid()))

    cli()


if __name__ == "__main__":
    main()
