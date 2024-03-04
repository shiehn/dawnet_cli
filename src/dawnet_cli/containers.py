import click
import docker
import os
from .persistence import save_pid, update_status

remote_name = "HEllO DOCKER"

def get_docker_client():
    try:
        client = docker.from_env()
        client.ping()  # This method checks if Docker daemon is accessible
        return client
    # except docker.errors.DockerException as e:
    #     click.echo(f"Failed to connect to Docker: {e}", err=True)
    #     click.get_current_context().exit(1)
    except Exception as e:
        #click.echo(f"An error occurred: {e}", err=True)
        #click.get_current_context().exit(1)
        return None


# click.echo(f"Failed to connect to Docker: {e}", err=True)
# click.get_current_context().exit(1)

def docker_check():
    client = get_docker_client()  # This will exit if Docker is not accessible
    if client is None:
        return False

    return True


def start_container(image_name, command=None, name=None):
    # Start a Docker container
    container = get_docker_client().containers.run(image_name, command=command, name=name, detach=True)
    print(f"Container {container.id} started.")

    # Get PID of the running container
    container.reload()  # Reload to update attributes
    pid = container.attrs['State']['Pid']

    # Persist PID in SQLite database
    save_pid(pid, container.id, remote_name, 1)

    return container


def stop_container(container_id):

    print(f"STOPPING Container {container_id}.")
    # Stop a Docker container
    container = get_docker_client().containers.get(container_id)
    container.stop()
    print(f"Container {container_id} stopped.")

    status = 0 # STOPPED
    update_status(container_id, status)

    return container


def capture_logs(container_id, log_file_path):
    # Capture container's stdout/stderr to a file
    container = get_docker_client().containers.get(container_id)
    logs = container.logs(stream=True)

    with open(log_file_path, 'wb') as log_file:
        for chunk in logs:
            log_file.write(chunk)


if __name__ == "__main__":
    # Example usage
    image_name = 'your_image_name_here'
    command = 'your_command_here'
    container_name = 'your_container_name_here'

    # Start container
    container = start_container(image_name=image_name, command=command, name=container_name)

    # Stop container (for demonstration, you might want to add a delay or a condition here)
    stop_container(container.id)

    # Capture logs
    log_file_path = f'{container_name}_logs.txt'
    capture_logs(container.id, log_file_path)
