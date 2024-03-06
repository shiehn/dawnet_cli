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

### Installation:
 
```python
sudo pip install -U dawnet-cli
```

### Usage:

```python
dawnet -h
```

**Note:** The CLI will point to the public DAWnet server by default (http://34.135.228.111:8081).  If you are running a private server, you will need to set the environment variable `DN_CLI_API` to the URL of your server with the port.


