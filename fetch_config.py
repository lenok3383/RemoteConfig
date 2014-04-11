import os.path
from optparse import OptionParser
import sys
import re
import logging

def get_info_from_file(path):
    info_list = []
    data_dict = {}
    # for file in path:
    with open(path, 'r') as file:
        for line in file:
            new_line = re.search(r'(?P<user>[A-z\d]+)@(?P<host>[A-z\d]+)(:(?P<port>\d*))? (?P<password>[A-z\d]+) (?P<command>[A-z]*)', line)
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
    parser.add_option("-h", "--host", dest="host", )
    parser.add_option("-u", "--username", dest="username", )
    parser.add_option("-po", "--port", dest="port", )
    parser.add_option("-c", "--command", dest="command", )
    parser.add_option("-pas", "--pass", type="string", dest="password")
    parser.add_option("-p", "--path", type="string", dest="path")
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
        if not options.password:
            print "Enter password"
            return
        info_dict = {
            'username':options.username,
            'host': options.host,
            'password': options.password,
            'command': options.command,
        }
        if options.port:
            info_dict['port'] = options.port
        info_list.append(info_dict)
    return info_list

class RemoteMachine():
    def __init__(self, info_dict):

        pass

    def get_info_from_remote_machine(self,command):
        pass

if __name__ == '__main__':
    main()

