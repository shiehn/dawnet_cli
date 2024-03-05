import time

from .models import RemoteContainer, RemoteImage
from .persistence import get_container_states


def get_remote_sources() -> []:

    #remote_name: str, source_url: str, remote_version: str):

    db_remote_source = RemoteSource(remote_name='Hello Remote', source_url='https://raw.githubusercontent.com/shiehn/dawnet-remotes/main/DAWNet_Remote_template.ipynb', remote_version='v0')


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

def get_remote_images() -> []:
    # stevehiehn/hello-dawnet
    # remote_name: str, image_name: str, remote_version: str

    db_remote_image = RemoteImage(remote_name="hello dawnet", image_name="stevehiehn/hello-dawnet", remote_version="1")

    return [db_remote_image]


def pull_remote_source():
    import requests

    # URL of the raw content
    file_url = 'https://raw.githubusercontent.com/shiehn/dawnet-remotes/main/DAWNet_Remote_template.ipynb'

    # The local path where you want to save the file
    file_name = 'DAWNet_Remote_template.ipynb'

    # Send a GET request to the file URL
    response = requests.get(file_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Open file in binary write mode and save the content to the local file
        with open(file_name, 'wb') as file:
            file.write(response.content)
        print(f'File "{file_name}" has been downloaded successfully.')
    else:
        print(f'Failed to download the file. Status code: {response.status_code}')
