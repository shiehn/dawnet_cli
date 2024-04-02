import os
import requests

from .config import URL_API, URL_AUTH
from .models import RemoteImage, RemoteSource
from .persistence import get_access_token


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


def publish_remote_source(
    remote_name,
    remote_description,
    remote_category,
    processor,
    source_url,
    colab_url=None,
    remote_version=None,
):
    """
    Publish a new remote source by making a POST request to the /remote-sources/ endpoint.

    Parameters:
    - base_url (str): The base URL where the /remote-sources/ endpoint is located.
    - remote_name (str): The name of the remote source.
    - remote_description (str): A description of the remote source.
    - remote_category (str): The category of the remote source.
    - source_url (str): The URL to the source.
    - colab_url (str, optional): The URL to a Colab, if applicable.
    - remote_version (str, optional): The version of the remote source, if applicable.

    Returns:
    A requests.Response object containing the server's response to the HTTP request.
    """

    # Endpoint for the POST request
    endpoint = f"{URL_API}/api/hub/remote-sources/"

    # Construct the JSON body of the request
    data = {
        "remote_name": remote_name,
        "remote_description": remote_description,
        "remote_category": remote_category,
        "processor": processor,
        "remote_author": "placeholder",
        "source_url": source_url,
        "colab_url": colab_url,
        "remote_version": remote_version,
    }

    # Remove keys with None values
    data = {k: v for k, v in data.items() if v is not None}

    access_token = get_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # Make the POST request
    response = requests.post(endpoint, headers=headers, json=data)

    # Return the response object
    return response


def insert_remote_image_info(image_info, access_token):
    route = "/api/hub/remote-images/"
    endpoint_url = f"{URL_API}{route}"
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        response = requests.post(endpoint_url, headers=headers, json=image_info)
        response.raise_for_status()  # This will raise an exception for HTTP errors
        return True
    except requests.RequestException as e:
        print("DATA: ", image_info)
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
def delete_elixir(remote_image_id):
    delete_url = f"{URL_API}/api/hub/remote-images/{remote_image_id}/"

    access_token = get_access_token()

    print("access_token: ", access_token)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    response = requests.delete(delete_url, headers=headers)

    # Checking the response
    if response.status_code == 204:
        print("RemoteImage deleted successfully.")
    else:
        print(f"Failed to delete RemoteImage. Status code: {response.status_code}")


def get_remote_images() -> []:
    response = requests.get(f"{URL_API}/api/hub/remote-images/")
    remote_images_data = response.json()

    remote_images = [
        RemoteImage(
            remote_name=item["remote_name"],
            remote_description=item["remote_description"],
            image_name=item["image_name"],
            remote_version=item["remote_version"],
            id=item["id"],
        )
        for item in remote_images_data
    ]

    return remote_images


def delete_remote_source(remote_source_id):
    delete_url = f"{URL_API}/api/hub/remote-sources/{remote_source_id}/"

    access_token = get_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    response = requests.delete(delete_url, headers=headers)

    # Checking the response
    if response.status_code == 204:
        print("RemoteSource deleted successfully.")
    else:
        print(
            f"Failed to delete RemoteSource. Status code: {response.status_code}, Detail: {response.text}"
        )


def get_remote_sources() -> []:
    list_sources_url = f"{URL_API}/api/hub/remote-sources/"

    response = requests.get(list_sources_url)
    remote_images_data = response.json()

    remote_sources = [
        RemoteSource(
            remote_name=item["remote_name"],
            remote_description=item["remote_description"],
            source_url=item["source_url"],
            remote_version=item["remote_version"],
            id=item["id"],
        )
        for item in remote_images_data
    ]

    return remote_sources


def verify_token(token):
    # Attempt to obtain token pair
    response = requests.post(
        f"{URL_AUTH}/auth/token/verify",
        json={"token": token},
    )

    return response.status_code == 200
