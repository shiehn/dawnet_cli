import sys

import click
import docker
from docker.models.containers import Container
import os
from .persistence import save_container_state, update_container_state, read_token_from_db
import warnings
import subprocess
import json


def check_nvidia_docker_installed():
    try:
        # Run 'docker info' and capture the output
        result = subprocess.run(['docker', 'info', '--format', '{{json .}}'], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            docker_info = json.loads(result.stdout)

            # Check for 'nvidia' in Runtimes
            if 'Runtimes' in docker_info and 'nvidia' in docker_info['Runtimes']:
                return True
            else:
                return False
        else:
            print(f"Error running 'docker info': {result.stderr}")
            return False
    except Exception as e:
        print(f"Exception occurred: {e}")
        return False


def format_image_name(input_str: str) -> str:
    """
    This function takes a string, replaces spaces with hyphens, removes any non-alphanumeric characters (excluding hyphens),
    and converts the string to lowercase.

    :param input_str: The input string to format.
    :return: A formatted, lowercase string with spaces replaced by hyphens and non-alphanumeric characters removed.
    """
    # Replace spaces with hyphens
    formatted_str = input_str.replace(" ", "-")

    # Remove non-alphanumeric characters (excluding hyphens)
    formatted_str = ''.join(char for char in formatted_str if char.isalnum() or char == '-')

    # Convert to lowercase
    formatted_str = formatted_str.lower()

    return formatted_str


def get_docker_client():
    try:
        client = docker.from_env()
        client.ping()  # This method checks if Docker daemon is accessible
        return client
    # except docker.errors.DockerException as e:
    #     click.echo(f"Failed to connect to Docker: {e}", err=True)
    #     click.get_current_context().exit(1)
    except Exception as e:
        # click.echo(f"An error occurred: {e}", err=True)
        # click.get_current_context().exit(1)
        return None


# click.echo(f"Failed to connect to Docker: {e}", err=True)
# click.get_current_context().exit(1)

def docker_check():
    client = get_docker_client()  # This will exit if Docker is not accessible
    if client is None:
        return False

    return True


def start_container(image_name: str, remote_name: str, remote_description: str, token: str, gpu: bool = False,
                    command=None, name=None) -> Container:
    # Check for GPU support if required
    if gpu and not check_nvidia_docker_installed():
        click.echo(
            "Error: GPU requested but the `nvidia-docker` extension was not found on this machine. Please follow Nvidia's install instructions: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html")
        return None

    # Get Docker client
    client = docker.from_env()

    # Device requests for GPU
    device_requests = None
    if gpu:
        device_requests = [docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])]

    # Run the container
    container = client.containers.run(
        image_name,
        command=command,
        name=name,
        detach=True,
        environment={
            'DN_CLI_TOKEN': token
        },
        device_requests=device_requests  # Add device requests here
    )

    # Get PID of the running container
    container.reload()  # Reload to update attributes
    pid = container.attrs['State']['Pid']

    print(f"Container started with Token: {token}")

    # Persist PID in SQLite database
    save_container_state(pid=pid,
                         container_id=container.id,
                         remote_name=remote_name,
                         remote_description=remote_description,
                         associated_token=token,
                         status=1)
    # save_container_state(pid, container.id, remote_name, token, 1)

    return container


def is_container_running(container_id):
    try:
        container = get_docker_client().containers.get(container_id)
        return container.status == 'running'
    except docker.errors.NotFound:
        # Handle the case where the container does not exist
        return False


def stop_container(container_id):
    print(f"STOPPING Container {container_id}.")
    # Stop a Docker container
    try:
        container = get_docker_client().containers.get(container_id)
        container.stop()
    except:
        print(f"Error Stopping container: {container_id}")
        return

    print(f"Container {container_id} stopped.")

    status = 0  # STOPPED
    update_container_state(container_id, status)

    return container


def build_image(image_name: str, path_to_dockerfile: str):
    """
    Build a Docker image from a Dockerfile.

    :param image_name: Name of the Docker image to be built.
    :param path_to_dockerfile: Path to the directory containing the Dockerfile.
    :return: Name of the built Docker image if successful, None otherwise.
    """
    client = get_docker_client()
    if client is None:
        print("Failed to get Docker client.")
        return None

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            # The build path is expected to be a directory containing the Dockerfile
            image, build_log = client.images.build(path=path_to_dockerfile, tag=image_name, rm=True)
            for line in build_log:
                # This will print the build logs to stdout. You can modify as needed.
                if 'stream' in line:
                    print(line['stream'].strip())

            print(f"Image {image_name} built successfully.")
            return image_name
        except docker.errors.BuildError as build_error:
            print(f"Failed to build Docker image: {build_error}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    return None


def capture_logs(container_id, log_file_path):
    # Capture container's stdout/stderr to a file
    container = get_docker_client().containers.get(container_id)
    logs = container.logs(stream=True)

    with open(log_file_path, 'wb') as log_file:
        for chunk in logs:
            log_file.write(chunk)


def tail_logs(container_id):
    # Tail container's stdout/stderr to the terminal
    container = get_docker_client().containers.get(container_id)
    logs = container.logs(stream=True, follow=True)

    for chunk in logs:
        print(chunk.decode('utf-8'), end='')
