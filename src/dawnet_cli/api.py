import time

from .models import Container
from .persistence import get_container_states


def get_remotes() -> []:


    db_container = Container(1, 1, 1, "Hello-Docker", 0)


    #
    # pids = list_pids(status=None)
    # print(f"Num Of PIDS: {len(pids)}")
    # for pid in pids:
    #     print(f"PID: {pid}")

    return [db_container]

    # return [
    #     'Music Gen - style transfer',
    #     'Demucs - stem splitting',
    #     'BeatNet - bpm detection',
    # ]