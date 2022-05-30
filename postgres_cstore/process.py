import subprocess


class Process(object):
    """Process class.
    """
    @staticmethod
    def run(cmd: str) -> str:
        """Run a external command as subprocess.
        :param cmd: str. an external command.
        :return: str.
            A stdout of subprocess.run() if return_code is 0. It raises exception if return_code is not 0.
        """
        return_code, output = Process._parse(subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
        if return_code != 0:
            # The output has error message of stderr if returncode is not 0.
            raise Exception(output)
        return output

    @staticmethod
    def _parse(complete_process: subprocess.CompletedProcess) -> (int, str):
        """Parse return of Process.run(cmd).
        :param complete_process: subprocess.CompleteProcess.
            This instance has three attributions, args, returncode and stdout.
            An args is equal to cmd as an argument subprocess.run(). A returncode has subprocess return code.
            A stdout has outputs of cmd executed subprocess.run().
        :return: (int, str).
            This is a tuple of subprocess.CompleteProcess.retruncode and subprocess.CompleteProcess.stdout.
            A returncode has return code as int. A stdout has outputs as string.
        """
        return complete_process.returncode, complete_process.stdout.decode('utf-8').strip()
