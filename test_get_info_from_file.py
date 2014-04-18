from unittest import TestCase
from fetch_config import get_info_from_file
import tempfile
import os



class TestGet_info_from_file(TestCase):


    def create_file(self, content):
        temp = tempfile.NamedTemporaryFile(delete=False)
        try:
            temp.writelines(content)
            temp.seek(0)
        finally:
            temp.close()
        return temp.name


    def test_get_info_from_empty_file(self):
        path = self.create_file('')
        res = get_info_from_file(path)
        self.assertEqual(res, [{}])

    def test_get_info_from_file(self):
        path = self.create_file('text only')
        res = get_info_from_file(path)
        self.assertEqual(res, [{}])


    def test_get_info_from_not_exist_file(self):
        path = 'NOT_EXISTING_PATH'
        self.assertRaises(IOError, get_info_from_file, path)

    def test_get_info_from_good_file_with_two_lines(self):
        path = self.create_file('user@host1:8984 qwert1 command\n user2@host2:69846 qwert2 comma\n')
        res = get_info_from_file(path)
        self.assertEqual(res, [{'username':'user1', 'host':'host1', 'port':'8984', 'password':'qwert1', 'command':'command'},
                                {'username':'user2', 'host':'host2', 'port':'69846', 'password':'qwert2', 'command':'comma'}])


    def test_get_info_from_good_file(self):
        path = self.create_file('user1@host1:451 qwert51 com\n some_text\n')
        res = get_info_from_file(path)
        self.assertEqual(res, [{'username':'user1', 'host':'host1', 'port':'451','password':'qwert51', 'command':'com'}])