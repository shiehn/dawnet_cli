class Container:
    def __init__(self, id, pid, container_id, remote_name, status):
        self.id = id
        self.pid = pid
        self.container_id = container_id
        self.remote_name = remote_name
        self.status = status

    def __repr__(self):
        return f"Container(id={self.id}, pid={self.pid}, container_id={self.container_id}, remote_name='{self.remote_name}', status='{self.status}')"
