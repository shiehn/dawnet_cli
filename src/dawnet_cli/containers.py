import docker
import os
from persistence import save_pid, delete_pid

# Connect to Docker
client = docker.from_env()


def start_container(image_name, command=None, name=None):
    # Start a Docker container
    container = client.containers.run(image_name, command=command, name=name, detach=True)
    print(f"Container {container.id} started.")

    # Get PID of the running container
    container.reload()  # Reload to update attributes
    pid = container.attrs['State']['Pid']

    # Persist PID in SQLite database
    save_pid(container.id, pid)

    return container


def stop_container(container_id):
    # Stop a Docker container
    container = client.containers.get(container_id)
    container.stop()
    print(f"Container {container_id} stopped.")

    # Remove PID entry from SQLite database
    delete_pid(container_id)

    return container


def capture_logs(container_id, log_file_path):
    # Capture container's stdout/stderr to a file
    container = client.containers.get(container_id)
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
