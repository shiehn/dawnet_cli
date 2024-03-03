# Use an official Bash image
FROM bash:latest

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy the script into the container
COPY hello_docker.sh .

# No need to change permissions in Dockerfile since we're ensuring it on the host
# Use bash to explicitly execute the script
CMD ["bash", "./hello_docker.sh"]
