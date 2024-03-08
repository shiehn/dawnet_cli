import os
import shutil
import tempfile
from urllib.request import urlopen
from docker import DockerClient
from urllib.parse import urlparse


class DockerImageBuilder:
    def __init__(self):
        self.docker_client = DockerClient.from_env()

    def download_file(self, url, destination_path):
        """Download a file from a URL to a specified local path."""
        with urlopen(url) as response, open(destination_path, "wb") as out_file:
            shutil.copyfileobj(response, out_file)

    def build_docker_image(self, notebook_source, image_name):
        """Build a Docker image from a Jupyter notebook URL."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Paths for the necessary files
            notebook_path = os.path.join(tmp_dir, "source.ipynb")
            startup_script_path = os.path.join(tmp_dir, "startup.sh")
            dockerfile_path = os.path.join(tmp_dir, "Dockerfile")

            # Check if notebook_source is a URL or a local file path and act accordingly
            if urlparse(notebook_source).scheme in ["http", "https"]:
                # notebook_source is a URL, download the Jupyter notebook
                self.download_file(notebook_source, notebook_path)
            else:
                # notebook_source is a local file path, copy the file
                shutil.copy(notebook_source, notebook_path)

            # Save the startup script
            with open(startup_script_path, "w") as startup_script:
                startup_script.write(
                    """#!/bin/bash
jupyter nbconvert --to notebook --execute /usr/src/app/source.ipynb --output /usr/src/app/executed_notebook.ipynb | tee /usr/src/app/notebook_log.txt
exec start-notebook.sh --NotebookApp.token='' --NotebookApp.password=''"""
                )

            # Create the Dockerfile
            with open(dockerfile_path, "w") as dockerfile:
                dockerfile.write(
                    """# Use the official Jupyter Notebook base image
FROM jupyter/base-notebook

# Install FFmpeg
USER root
RUN apt-get update && apt-get install -y ffmpeg

# Copy the notebook and the startup script into the container
COPY source.ipynb startup.sh /usr/src/app/

# Ensure the startup script is executable
RUN chmod +x /usr/src/app/startup.sh

# Adjust permissions to ensure `jovyan` can write to /usr/src/app
RUN chown -R jovyan:users /usr/src/app

# Switch back to jovyan to avoid permission issues
USER jovyan

# Set the working directory in the container
WORKDIR /usr/src/app

# Install nbconvert and necessary Python packages
RUN pip install nbconvert dawnet-client

# Expose the port the notebook runs on
EXPOSE 8888

# Use the custom startup script
CMD ["bash", "/usr/src/app/startup.sh"]
"""
                )
            # Build Docker image and print logs
            for chunk in self.docker_client.api.build(
                path=tmp_dir,
                tag=image_name,
                rm=True,
                nocache=True,
                dockerfile="Dockerfile",
                decode=True,
            ):
                if "stream" in chunk:
                    print(chunk["stream"].strip())
