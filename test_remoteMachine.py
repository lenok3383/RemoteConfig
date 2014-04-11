import unittest
from shared.testing.vmock.mockcontrol import MockControl
import pexpect
from fetch_config import RemoteMachine, TimeoutException, WrongPassword

class TestRemoteMachine(unittest.TestCase):
    def test___init__(self):
        pass


    def setUp(self):
        self.mc = MockControl()

    def tearDown(self):
        self.mc.tear_down()

    def test_good_connection(self):
        my_dict = {'username':'lenok',
                  'host':'host',
                  'port':'port',
                  'password':'123',
                  'command':'command'}

        spawn_mock = self.mc.mock_class(pexpect.spawn)
        spawn_ctor_mock = self.mc.mock_constructor(pexpect, 'spawn')

        spawn_ctor_mock(my_dict).returns(spawn_mock)

        spawn_mock.expect(['password:', 'Connection timed out']).returns(0)
        spawn_mock.sendline('123')
        spawn_mock.expect([':~\$','password']).returns(0)

        self.mc.replay()

        RemoteMachine(my_dict)

        self.mc.verify()

    def test_timeout_connection(self):
        my_dict = {'username':'lenok',
                  'host':'host',
                  'port':'port',
                  'password':'123',
                  'command':'command'}

        spawn_mock = self.mc.mock_class(pexpect.spawn)
        spawn_ctor_mock = self.mc.mock_constructor(pexpect, 'spawn')

        spawn_ctor_mock(my_dict).returns(spawn_mock)

        spawn_mock.expect(['password:', 'Connection timed out']).returns(1)

        self.mc.replay()

        self.assertRaises(TimeoutException, RemoteMachine , my_dict)

        self.mc.verify()


    def test_perm_denied_connection(self):
        test_dict = {'username':'lenok',
                  'host':'host',
                  'port':'port',
                  'password':'password',
                  'command':'command'}

        spawn_mock = self.mc.mock_class(pexpect.spawn)
        spawn_ctor_mock = self.mc.mock_constructor(pexpect, 'spawn')

        spawn_ctor_mock(test_dict).returns(spawn_mock)

        spawn_mock.expect(['password:', 'Connection timed out']).returns(0)
        spawn_mock.sendline('password')
        spawn_mock.expect([':~\$','password']).returns(1)

        self.mc.replay()

        self.assertRaises(WrongPassword, RemoteMachine, test_dict)

        self.mc.verify()





