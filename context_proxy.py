import os
import re
import subprocess

import requests

APP_STATIC_PORTS = os.getenv('APP_STATIC_PORTS', "80/TCP")
APP_LISTENER = os.getenv('APP_LISTENER', "0.0.0.0")
APP_CFG_PATH = os.getenv('APP_CFG_PATH', "/app/config.cfg")


class ArbitriumContextGetter:
    ENV_CONTEXT_URL = "ARBITRIUM_CONTEXT_URL"
    ENV_CONTEXT_TOKEN = "ARBITRIUM_CONTEXT_TOKEN"

    def __init__(self, url: str, token: str):
        self.url = url
        self.token = token
        self.context = {}

    def __get_headers(self) -> dict:
        return {
            'authorization': self.token
        }

    def get_context(self) -> dict:
        context = {}

        reply = requests.get(self.url, headers=self.__get_headers())

        if reply.status_code == 200:
            context = reply.json()
            request_id = context.get('request_id')
            print(f"Received Context for request #{request_id}")

        return context

    @staticmethod
    def create_from_env():
        context_url = os.getenv(ArbitriumContextGetter.ENV_CONTEXT_URL)
        context_token = os.getenv(ArbitriumContextGetter.ENV_CONTEXT_TOKEN)

        if context_url and context_token:
            print(f"Generating Context Getter to this url {context_url} with a token of length={len(context_token)}")
            return ArbitriumContextGetter(url=context_url, token=context_token)


class ArbitriumContext:
    def __init__(self, request_id: str, public_ip: str, fqdn: str, ports: dict, **kwargs):
        self.request_id = request_id
        self.public_ip = public_ip
        self.fqdn = fqdn
        self.ports = ports
        self.options = kwargs

    @staticmethod
    def create_from_context(context: dict):
        return ArbitriumContext(**context)

    def get_port_mapping(self, port: int) -> int:
        port = self.ports.get(str(port), {})
        return port.get('external')


class PortMapping:
    def __init__(self, port, protocol):
        self.port = port
        self.protocol = protocol

        self.mapped_port = None

    @staticmethod
    def create_from_env(string):
        port_proto = string.split('/')
        if len(port_proto) == 2:
            return PortMapping(port_proto[0], protocol=port_proto[1])


class ConfigurationUpdater:
    @staticmethod
    def __split_ports(string: str):
        ports = []

        for port_proto in string.split(','):
            port_mapping = PortMapping.create_from_env(port_proto)
            if port_mapping:
                ports.append(port_mapping)

        return ports

    def __init__(self, arbitrium_context: ArbitriumContext):
        self.context = arbitrium_context
        self.path = APP_CFG_PATH
        self.ports = ConfigurationUpdater.__split_ports(APP_STATIC_PORTS)
        self.default_ip = APP_LISTENER

        self.public_ip = self.context.public_ip

        for port in self.ports:
            port.mapped_port = self.context.get_port_mapping(port.port)

    def inject_configuration(self) -> bool:
        success = False

        if os.path.isfile(self.path):
            print(f"Injecting Configuration to file {self.path}")
            for port in self.ports:
                print(f"Mapping IP[{self.public_ip}] and PORT[{port.mapped_port}:{port.port}]")

            with open(self.path, 'r+') as file:
                content = file.read()

                for port in self.ports:
                    content = re.sub(str(port.port), str(port.mapped_port), content)

                content = re.sub(self.default_ip, self.public_ip, content)

                file.seek(0)
                file.write(content)
                file.truncate()
                file.close()
                success = True

            print("Injection done!")
        else:
            print(f"No File Detected here: {self.path}")

        return success


class ProxyProcess:
    def __init__(self, instance_port, listener_port, proto: str):
        self.instance_port = instance_port
        self.listener_port = listener_port
        self.port_type = proto.lower()

        self.socat_name = 'socat'
        self.socat_listener = f"{self.port_type}-listen:{self.instance_port},fork,reuseaddr"
        self.socat_sender = f"{self.port_type}:127.0.0.1:{self.listener_port}"

    def start(self):
        print("Starting Socat Proxy")

        process = subprocess.Popen(
            ["nohup", self.socat_name, self.socat_listener, self.socat_sender]
        )
        pid = process.pid

        if isinstance(pid, int):
            print(f"Socat Proxy started {self.instance_port}:{self.listener_port} with PID: {pid}")
        else:
            print("Failed to start the Socat Proxy")


def main():
    arbitrium_context_getter = ArbitriumContextGetter.create_from_env()

    if arbitrium_context_getter:
        print("Getting the Context")
        context = arbitrium_context_getter.get_context()
        arbitrium_context = ArbitriumContext.create_from_context(context=context)
        configuration = ConfigurationUpdater(arbitrium_context=arbitrium_context)
        configuration_success = configuration.inject_configuration()

        if configuration_success:
            for port in configuration.ports:
                proxy = ProxyProcess(port.port, port.mapped_port, port.protocol)
                proxy.start()

            print("Ready to boot up the server!")

    else:
        print("Impossible to create the Arbitrium Context Getter, please activate 'Inject Context' in Arbitrium")


if __name__ == '__main__':
    print("Script to get Context from Arbitrium is starting")
    main()
