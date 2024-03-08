# DAWnet CLI
A python CLI used to setup &amp; manage [DAWnet](https://dawnet.tools/) remote scripts on MAC, LINUX and Servers

### Requirements:

- ensure Python >= 3.x is installed
```python
python --version
```

- ensure Pip is installed
```python
pip list
```

- ensure [Docker](https://www.docker.com/) is installed
```python
which docker
```

- (if you plan to run GPU dependent functions) ensure [Nvidia Docker Extention](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) is installed

### Installation:
 
```python
sudo pip install -U dawnet-cli
```

### Usage:

```python
dawnet
```

**Note:** The CLI will point to the public DAWnet server by default (http://34.135.228.111:8081).  If you are running a private server, you will need to set the environment variable `DN_CLI_API` to the URL of your server with the port.


