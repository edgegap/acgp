# Arbitrium Context Getter && Proxy (ACGP)

This small project is an example of how you can inject Arbitrium's Context inside a running Deployment and reverse the port.
Mapping from Dynamic/Static Ports with a Socat Stream

### Prerequisites

- [Python 3.7](https://www.python.org/downloads/release/python-370/)
- [Docker](https://docs.docker.com/get-docker/)

## Building

- Clone the Repo

```
git clone <GIT_URL>
```

- Move into the folder

```
cd acgp
```

- Build the project

```
docker build -t acgp:version .
```

- Tag and Push to a private repository

```
docker tag acgp:version your/private/repo/acgp:version
docker push your/private/repo/acgp:version
```

## Upload Your image to Arbitrium

Click on the link for the documentation for Arbitrium on create your game profile. You will need to activate the
option ***Inject context***

[Upload your Image to Arbitrium](http://docs.edgegap.com/docs/arbitrium/step-2)

## What the Script will do

### Send a Request to Arbitrium

by reading injected environment variables from Arbitrium to get ARBITRIUM_CONTEXT_URL and ARBITRIUM_CONTEXT_TOKEN the
script will call Arbitrium to get the Context

### Overriding Your Configuration File

now that we have the context with the external/internal mapping, the script will override every single value that
contains the port or the instance listener to public ip/port using the path given with **APP_CFG_PATH**

For example, if you have set APP_LISTENER to 1.2.3.4 and port 80/TCP:

```
listen 1.2.3.4:80;
listen [::]80;
```

given a dynamic port mapping 30123->80 and public_ip=43.21.0.123

your config will become

```
listen 43.21.0.123:30123;
listen [::]30123;
```

### Starting a Socat Stream to map *external:internal:listener*
for every port mapped in **APP_STATIC_PORTS** a socat stream will be started in a background process

for Example given port 80/TCP and 443/TCP with public ip to 12.34.56.78

- 30400 -> 80
- 30401 -> 443

you will have two streams inside your container.

- 0.0.0.0:80->127.0.0.1:30400
- 0.0.0.0:443->127.0.0.1:30401

The full mapping for Container Configured with 80/TCP,443/TCP will be

- EXTERNAL->INTERNAL->LISTENER
- 12.34.56.78:30400->0.0.0.0:80->127.0.0.1:30400
- 12.34.56.78:30401->0.0.0.0:443->127.0.0.1:30401

## Map The port

You can modify the **context_proxy.py** directly or inject ENV from our platform.

Imagine you have ports **1234/TCP** and **4444/UDP**

Example of script modification:

```
APP_STATIC_PORTS = os.getenv('APP_STATIC_PORTS', "1234/TCP,4444/UDP")
APP_LISTENER = os.getenv('APP_LISTENER', "0.0.0.0")
APP_CFG_PATH = os.getenv('APP_CFG_PATH', "/app/config.cfg")
```

Example with our platform on App Version Creation/Update with the API:

```
{
    [...] # Collapsed Body
    "envs": [
        {
            "key": "APP_STATIC_PORTS",
            "value": "1234/TCP,4444/UDP",
            "is_secret": false
        },
        {
            "key": "APP_LISTENER",
            "value": "0.0.0.0",
            "is_secret": false
        },
        {
            "key": "APP_CFG_PATH",
            "value": "/app/config.cfg",
            "is_secret": false
        }
    ]
}
```

## Authors

* **Bastien Roy-Mazoyer**

## License

MIT License

Copyright (c) [2021] [Edgegap Technologies Inc.]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
