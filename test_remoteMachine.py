import unittest
from shared.testing.vmock.mockcontrol import MockControl
import fetch_config
import pexpect
from fetch_config import RemoteMachine


class TestRemoteMachine(unittest.TestCase):
    def test___init__(self):
        pass


    def setUp(self):
        self.mc = MockControl()

    def tearDown(self):
        self.mc.tear_down()

    def test_good_connection(self):
        mc = MockControl()

        spawn_mock = mc.mock_class(pexpect.spawn)
        spawn_ctor_mock = mc.mock_constructor(pexpect, 'spawn')

        spawn_ctor_mock(1).returns(spawn_mock)

        spawn_mock.expect(['password:', 'Connection timed out']).returns(0)
        spawn_mock.sendline('123')
        spawn_mock.expect([':~\$','Permission denied']).returns(0)
        # spawn_mock.sendline('ifconfig')

        mc.replay()

        # child = pexpect.spawn('ssh %s %s %s'%( 'lenok', 'host', 'port'))

        # spawn_mock = pexpect.spawn(1)
        RemoteMachine({'lenok', 'host', 'port','command'})
        # test_result =
        mc.verify()

        # my_result = ['result']
        # self.assertListEqual(test_result,my_result)
