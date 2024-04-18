![signals_and_sorcery_logo](https://storage.googleapis.com/docs-assets/sas_runes_cli_2.png)
# RUNES CLI
A python CLI used to setup &amp; manage [Crucible Plugins](https://signalsandsorcery.app/) remote scripts on MAC, LINUX and Servers

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
sudo pip install -U runes-cli
```

### Usage:

```python
runes
```

**Note:** The CLI will point to the public `Signals & Sorcery` server by default (https://signalsandsorceryapi.com).  If you are running a private server, there are three configurable values:

- `DN_CLI_API` - The domain/ip of the server
- `DN_CLI_AUTH` - The domain/ip of the authentication server 




