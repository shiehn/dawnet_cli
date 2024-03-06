class RemoteContainer:
    def __init__(self, id: int = 0, pid: int = 0, container_id: str = '', remote_name: str = '',
                 remote_description: str = '', associated_token: str = None, status: int = 0, ):
        self.id = id
        self.pid = pid
        self.container_id = container_id
        self.remote_name = remote_name
        self.remote_description = remote_description
        self.associated_token = associated_token
        self.status = status

    def __repr__(self):
        return f"RemoteContainer(id={self.id}, pid={self.pid}, container_id={self.container_id}, remote_name='{self.remote_name}, remote_description={self.remote_description}, associated_token='{self.associated_token}', status='{self.status}')"


class RemoteImage:
    def __init__(self, remote_name: str, remote_description: str, image_name: str, remote_version: str):
        self.remote_name = remote_name
        self.remote_description = remote_description
        self.image_name = image_name
        self.remote_version = remote_version


class RemoteSource:
    def __init__(self, remote_name: str, remote_description: str, source_url: str, remote_version: str):
        self.remote_name = remote_name
        self.remote_description = remote_description
        self.source_url = source_url
        self.remote_version = remote_version
