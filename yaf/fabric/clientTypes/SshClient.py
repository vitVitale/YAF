from paramiko import SSHClient, AutoAddPolicy
from yaf.utils.common_constants import RESOURCES_DIR


class SSHCl:
    def __init__(self, config: dict):
        config.pop('name')
        self.conf = config
        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())

    def _connect(self):
        self.client.connect(**self.conf)
        self.sftp = self.client.open_sftp()
        self.ssh = self.client.invoke_shell()

    def _shutdown(self):
        self.client.close()

    def execute_cmd(self, commands: str):
        self._connect()
        stdin, stdout, stderr = self.client.exec_command(commands)
        data = stdout.read() + stderr.read()
        result = data.decode('UTF-8').replace('', '').strip()
        self._shutdown()
        return result

    def download_file(self, remote_file):
        self._connect()
        self.sftp.get(remotepath=remote_file,
                      localpath=f"{RESOURCES_DIR}/{remote_file[remote_file.rfind('/') + 1:]}")
        self._shutdown()
