import os.path
from optparse import OptionParser
import sys
import re
import logging
import pexpect
import threading
import getpass


def get_info_from_file(path):
    info_list = []
    data_dict = {}
    with open(path, 'r') as file:
        for line in file:
            new_line = re.search(
                r'(?P<user>[A-z\d]+)@(?P<host>[A-z\d]+)(:(?P<port>\d*))? (?P<password>[A-z\d]+) (?P<command>[A-z]*)',
                line)
            if not new_line:
                logging.error('Problem: Check input info in line:%s', line)
                continue
            data_dict = {
                'username': new_line.group('user'),
                'host': new_line.group('host'),
                'password': new_line.group('password'),
                'command': new_line.group('command'),
            }
            if new_line.group('port'):
                data_dict['port'] = new_line.group('port')
            info_list.append(data_dict)
    return info_list


def main():
    info_list = []
    info_dict = {}
    parser = OptionParser()
    parser.add_option("--host", dest="host")
    parser.add_option("-u", "--username", type="string", dest="username")
    parser.add_option("--port", dest="port")
    parser.add_option("-c", "--command", dest="command")
    # parser.add_option("-p", "--pass", type="string", dest="password")
    parser.add_option("--path", type="string", dest="path")
    (options, args) = parser.parse_args(sys.argv)
    if options.path:
        info_list = get_info_from_file(options.path)
    else:
        if not options.host:
            print "Enter host"
            return
        if not options.username:
            print "Enter username"
            return
        if not options.command:
            print "Enter command"
            return
        password = getpass.getpass()
        info_dict = {
            'username': options.username,
            'host': options.host,
            'password': password,
            'command': options.command,
        }
        if options.port:
            info_dict['port'] = options.portrem
        info_list.append(info_dict)
    result_list = []
    threads = []
    for items in info_list:
        thread = RemoteCommandThread(items)
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
        result_list.append(thread.get_result_value())
    for items in (result_list):
        print "Command output:", items


class RemoteMachine():
    DEFAULT_SSH_PORT = 22
    SSH_COMMAND = 'ssh {username}@{host} -p {port}'
    SHELL_PROMPT = r':~\$'
    PASSWORD_PROMPT = r'password:'
    TIMEOUT_PROMPT = r'Connection timed out'
    UNKNOWN_PROMPT = r'Name or service not known'

    def __init__(self, info_dict):
        self.child = self.establish_connection(info_dict)

    def establish_connection(self, info_dict):
        for key in ('username', 'host', 'password'):
            if not key in info_dict:
                raise ValueError('There isn\'t some key of info')

        if not 'port' in info_dict:
            info_dict['port'] = self.DEFAULT_SSH_PORT

        ssh_command = self.SSH_COMMAND.format(**info_dict)

        child = pexpect.spawn(ssh_command)
        expect_options = [self.PASSWORD_PROMPT, self.UNKNOWN_PROMPT, self.TIMEOUT_PROMPT,
                          self.SHELL_PROMPT]
        pass_option = [self.SHELL_PROMPT, self.PASSWORD_PROMPT]

        i = child.expect(expect_options)
        if expect_options[i] == self.PASSWORD_PROMPT:
            child.sendline(info_dict['password'])
            p = child.expect(pass_option)
            if pass_option[p] == self.PASSWORD_PROMPT:
                child.close(True)
                raise WrongPassword('This password is wrong')
        elif expect_options[i] == self.UNKNOWN_PROMPT:
            child.close(True)
            raise CannotConnectToMachine('Name or service not known')
        elif expect_options[i] == self.TIMEOUT_PROMPT:
            child.close(True)
            raise TimeoutException('Connection timed out')
        return child

    def get_info_from_remote_machine(self, command):
        if not self.child.isalive():
            raise TerminationConnection('Connection failed')
        self.child.sendline(command)
        self.child.expect(self.SHELL_PROMPT)
        result = self.get_child_before()
        self.child.close(True)
        return result

    def get_child_before(self):
        return self.child.before


class RemoteCommandThread(threading.Thread):
    def __init__(self, info_dict):
        super(RemoteCommandThread, self).__init__()
        self.info_dict = info_dict
        self.command = self.info_dict['command']
        self.result = ""

    def run(self):
        connection = RemoteMachine(self.info_dict)
        self.result = connection.get_info_from_remote_machine(self.command)

    def get_result_value(self):
        return self.result


class TimeoutException(Exception):
    pass


class WrongPassword(Exception):
    pass


class CannotConnectToMachine(Exception):
    pass


class TerminationConnection(Exception):
    pass


if __name__ == '__main__':
    main()

