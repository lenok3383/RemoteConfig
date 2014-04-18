import unittest
from unittest import TestCase
from shared.testing.vmock.mockcontrol import MockControl
import pexpect
import fetch_config
from fetch_config import RemoteMachine, TimeoutException, WrongPassword, TerminationConnection, CannotConnectToMachine


class TestRemoteMachine(TestCase):
    def test_establish_connection(self):
        pass

    SHELL_PROMPT = r':~\$'
    PASSWORD_PROMPT = r'password:'
    TIMEOUT_PROMPT = r'Connection timed out'
    UNKNOWN_PROMPT = r'Name or service not known'

    def setUp(self):
        self.mc = MockControl()

    def tearDown(self):
        self.mc.tear_down()

    def test_good_connection(self):
        test_dict = {'username': 'lenok',
                     'host': 'host4',
                     'port': '23',
                     'password': '123',
                     'command': 'command'}
        ssh_com = 'ssh lenok@host4 -p 23'
        spawn_mock = self.mc.mock_class(pexpect.spawn)
        spawn_ctor_mock = self.mc.mock_constructor(pexpect, 'spawn')

        spawn_ctor_mock(ssh_com).returns(spawn_mock)

        spawn_mock.expect([self.PASSWORD_PROMPT, self.UNKNOWN_PROMPT, self.TIMEOUT_PROMPT,
                           self.SHELL_PROMPT]).returns(0)
        spawn_mock.sendline('123')
        spawn_mock.expect([self.SHELL_PROMPT, self.PASSWORD_PROMPT]).returns(0)

        self.mc.replay()

        result =  RemoteMachine(test_dict)

        self.mc.verify()


    def test_timeout_connection(self):
        test_dict = {'username': 'lenok',
                     'host': 'host4',
                     'port': '23',
                     'password': '123',
                     'command': 'command'}
        ssh_com = 'ssh lenok@host4 -p 23'
        spawn_mock = self.mc.mock_class(pexpect.spawn)
        spawn_ctor_mock = self.mc.mock_constructor(pexpect, 'spawn')

        spawn_ctor_mock(ssh_com).returns(spawn_mock)

        spawn_mock.expect([self.PASSWORD_PROMPT, self.UNKNOWN_PROMPT,
                           self.TIMEOUT_PROMPT, self.SHELL_PROMPT]).returns(2)
        spawn_mock.close(True)

        self.mc.replay()

        result = self.assertRaises(TimeoutException, RemoteMachine, test_dict)

        self.mc.verify()

    def test_wrong_password(self):
        test_dict = {'username': 'lenok',
                     'host': 'host4',
                     'port': '23',
                     'password': '23',
                     'command': 'command'}
        ssh_com = 'ssh lenok@host4 -p 23'
        spawn_mock = self.mc.mock_class(pexpect.spawn)
        spawn_ctor_mock = self.mc.mock_constructor(pexpect, 'spawn')

        spawn_ctor_mock(ssh_com).returns(spawn_mock)

        spawn_mock.expect([self.PASSWORD_PROMPT, self.UNKNOWN_PROMPT,
                           self.TIMEOUT_PROMPT, self.SHELL_PROMPT]).returns(0)
        spawn_mock.sendline('23')
        spawn_mock.expect([self.SHELL_PROMPT, self.PASSWORD_PROMPT]).returns(1)
        spawn_mock.close(True)

        self.mc.replay()

        self.assertRaises(WrongPassword, RemoteMachine, test_dict)

        self.mc.verify()

    def test_wrong_info(self):
        test_dict = {'username': 'lenok',
                     'host': 'host4',
                     'port': '23',
                     'password': '3',
                     'command': 'command'}
        ssh_com = 'ssh lenok@host4 -p 23'
        spawn_mock = self.mc.mock_class(pexpect.spawn)
        spawn_ctor_mock = self.mc.mock_constructor(pexpect, 'spawn')

        spawn_ctor_mock(ssh_com).returns(spawn_mock)

        spawn_mock.expect([self.PASSWORD_PROMPT, self.UNKNOWN_PROMPT,
                           self.TIMEOUT_PROMPT, self.SHELL_PROMPT]).returns(1)
        spawn_mock.close(True)

        self.mc.replay()

        self.assertRaises(CannotConnectToMachine, RemoteMachine, test_dict)

        self.mc.verify()

    def test_get_info_from_remote_machine(self):
        test_command = 'ifconfig'
        test_dict = {'username': 'lenok',
                     'host': 'host4',
                     'port': '23',
                     'password': '123',
                     'command': 'command'}

        spawn_mock = self.mc.mock_class(pexpect.spawn)
        mock_establish_connection = self.mc.mock_method(RemoteMachine, 'establish_connection')
        mock_establish_connection(test_dict).returns(spawn_mock)
        mock_get_child_before = self.mc.mock_method(RemoteMachine, 'get_child_before')

        spawn_mock.isalive().returns(True)
        spawn_mock.sendline(test_command)
        mock_get_child_before().returns('some text')
        spawn_mock.close(True)

        self.mc.replay()

        machine = RemoteMachine(test_dict)
        result = machine.get_info_from_remote_machine(test_command)

        self.mc.verify()

        self.assertEquals(result, 'some text')

    def test_get_info_from_remote_machine_termination_connection(self):
        test_command = 'ifconfig'
        test_dict = {'username': 'lenok',
                     'host': 'host4',
                     'port': '23',
                     'password': '123',
                     'command': 'command'}
        spawn_mock = self.mc.mock_class(pexpect.spawn)
        mock_establish_connection = self.mc.mock_method(RemoteMachine, 'establish_connection')

        mock_establish_connection(test_dict).returns(spawn_mock)

        spawn_mock.isalive().returns(False)

        self.mc.replay()

        machine = RemoteMachine(test_dict)
        self.assertRaises(TerminationConnection, machine.get_info_from_remote_machine,test_command)

        self.mc.verify()

