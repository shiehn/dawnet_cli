import os
import requests

from .models import RemoteImage, RemoteSource

base_url = os.getenv("DN_CLI_API", "https://signalsandsorceryapi.com")


def get_remote_sources() -> []:
    # remote_name: str, source_url: str, remote_version: str):

    db_remote_source = RemoteSource(
        remote_name="Hello Remote",
        source_url="https://raw.githubusercontent.com/shiehn/dawnet-remotes/main/DAWNet_Remote_template.ipynb",
        remote_version="v0",
    )

    #
    # pids = list_pids(status=None)
    # print(f"Num Of PIDS: {len(pids)}")
    # for pid in pids:
    #     print(f"PID: {pid}")

    return [db_remote_source]

    # return [
    #     'Music Gen - style transfer',
    #     'Demucs - stem splitting',
    #     'BeatNet - bpm detection',
    # ]


def insert_remote_image_info(image_info):
    route = "/api/hub/remote-images/"
    base_url = os.getenv("DN_CLI_API", "https://signalsandsorceryapi.com")
    endpoint_url = f"{base_url}{route}"
    try:
        response = requests.post(endpoint_url, json=image_info)
        response.raise_for_status()  # This will raise an exception for HTTP errors
        return True
    except requests.RequestException as e:
        print(f"Failed to register image information: {e}")
        return False


# http://localhost:8081/api/hub/remote-images/
# [
#     {
#         "id": "d7ae7bd2-45b3-4ca9-972b-5b5805158067",
#         "remote_name": "Hello DAWnet",
#         "remote_description": "DAWNet test image",
#         "remote_category": "template",
#         "remote_author": "Steve Hiehn",
#         "image_name": "stevehiehn/hello-dawnet",
#         "remote_version": "v0",
#         "created_at": "2024-03-06T06:13:38",
#         "updated_at": "2024-03-06T06:13:38"
#     }
# ]


def get_remote_images() -> []:
    response = requests.get(f"{base_url}/api/hub/remote-images/")
    remote_images_data = response.json()

    remote_images = [
        RemoteImage(
            remote_name=item["remote_name"],
            remote_description=item["remote_description"],
            image_name=item["image_name"],
            remote_version=item["remote_version"],
        )
        for item in remote_images_data
    ]

    # print(f"base_url: {base_url}")
    # print(f"Remote Images: {remote_images}")

    return remote_images


def get_remote_sources() -> []:
    response = requests.get(f"{base_url}/api/hub/remote-sources/")
    remote_images_data = response.json()

    remote_sources = [
        RemoteSource(
            remote_name=item["remote_name"],
            remote_description=item["remote_description"],
            source_url=item["source_url"],
            remote_version=item["remote_version"],
        )
        for item in remote_images_data
    ]

    # print(f"base_url: {base_url}")
    # print(f"Remote Images: {remote_sources}")

    return remote_sources


def pull_remote_source():
    # URL of the raw content
    file_url = "https://raw.githubusercontent.com/shiehn/dawnet-remotes/main/DAWNet_Remote_template.ipynb"

    # The local path where you want to save the file
    file_name = "DAWNet_Remote_template.ipynb"

    # Send a GET request to the file URL
    response = requests.get(file_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Open file in binary write mode and save the content to the local file
        with open(file_name, "wb") as file:
            file.write(response.content)
        print(f'File "{file_name}" has been downloaded successfully.')
    else:
        print(f"Failed to download the file. Status code: {response.status_code}")
