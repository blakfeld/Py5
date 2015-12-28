import os
import sys
import getpass
import unittest
try:
    from py5 import iControlREST
except ImportError:
    sys.path.append(
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from py5 import iControlREST


class py5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server = raw_input('Server: ')
        user = raw_input('User: ')
        pw = getpass.getpass()
        cls.py5 = iControlREST(server=server,
                               username=user,
                               password=pw,
                               verify=False,
                               debug=True)

    def test_partition_does_not_exist(self):
        self.assertEqual(404,
                         self.py5.get_partition('bogus_partition')['code'])

    def test_create_partition(self):
        self.assertEqual(
            'test_create_partition',
            self.py5.create_partition('/test_create_partition')['name'])
        self.py5.delete_partition('test_create_partition')

    def test_delete_partition(self):
        self.py5.create_partition('/test_delete_partition')
        self.assertEqual(
            {},
            self.py5.delete_partition('test_delete_partition'))

    def test_pool_does_not_exist(self):
        self.assertEqual(404, self.py5.get_pool('bogus_pool')['code'])

    def test_add_pool(self):
        self.assertEqual(
            'test_create_pool',
            self.py5.create_pool(name='test_create_pool')['name'])
        self.py5.delete_pool('test_create_pool')

    def test_delete_pool(self):
        self.py5.create_pool(name='test_delete_pool')
        self.assertEqual({}, self.py5.delete_pool(name='test_delete_pool'))

    def test_node_does_not_exist(self):
        self.assertEqual(404, self.py5.get_node('bogus_node')['code'])

    def test_add_node(self):
        self.assertEqual(
            'test_create_node',
            self.py5.create_node(name='test_create_node',
                                 address='123.123.123.123')['name'])
        self.py5.delete_node('test_create_node')

    def test_delete_node(self):
        self.py5.create_node(name='test_delete_node',
                             address='123.123.123.123')
        self.assertEqual({}, self.py5.delete_node(name='test_delete_node'))

    def test_disable_node(self):
        self.py5.create_node(name='test_disable_node',
                             address='123.123.123.123')
        self.assertEqual(
            'user-disabled',
            self.py5.disable_node(name='test_disable_node')['session'])
        self.py5.delete_node('test_disable_node')

    def test_enable_node(self):
        self.py5.create_node(name='test_enable_node',
                             address='123.123.123.123')
        self.py5.disable_node(name='test_enable_node')
        self.assertEqual(
            'monitor-enabled',
            self.py5.enable_node(name='test_enable_node')['session'])
        self.py5.delete_node('test_enable_node')

    def test_enable_pool_member(self):
        self.py5.create_node(name='test_enable_member_node',
                             address='123.123.123.123')
        self.py5.create_pool(name='test_enable_member_pool')
        self.py5.add_members_to_pool(
            target_pool='test_enable_member_pool',
            new_members=[{'name': 'test_enable_member_node:80'}])
        self.py5.disable_pool_member(name='test_enable_member_pool',
                                     member_name='test_enable_member_node')
        self.py5.enable_pool_member(name='test_enable_member_pool',
                                    member_name='test_enable_member_node:80')
        self.assertEqual(
            'user-enabled',
            self.py5.get_pool_members(name='test_enable_member_pool')
            ['items'][0]['session'])
        self.py5.remove_member_from_pool(target_pool='test_enable_member_pool',
                                         member_name='test_enable_member_node')
        self.py5.delete_node('test_enable_member_node')
        self.py5.delete_pool('test_enable_member_pool')

    def test_disable_pool_member(self):
        self.py5.create_node(name='test_disable_member_node',
                             address='123.123.123.123')
        self.py5.create_pool(name='test_disable_member_pool')
        self.py5.add_members_to_pool(
            target_pool='test_disable_member_pool',
            new_members=[{'name': 'test_disable_member_node:80'}])
        self.py5.disable_pool_member(
            name='test_disable_member_pool',
            member_name='test_disable_member_node:80')

        self.assertEqual(
            'user-disabled',
            self.py5.get_pool_members(name='test_disable_member_pool')
            ['items'][0]['session'])
        self.py5.remove_member_from_pool(
            target_pool='test_disable_member_pool',
            member_name='test_disable_member_node')
        self.py5.delete_node('test_disable_member_node')
        self.py5.delete_pool('test_disable_member_pool')

    def test_add_to_pool(self):
        self.py5.create_pool(name='test_add_members_pool')
        self.py5.create_node(name='test_add_members_node',
                             address='123.123.123.123')
        self.py5.add_members_to_pool(
            target_pool='test_add_members_pool',
            new_members=[{'name': 'test_add_members_node:80'}])
        self.assertEqual(
            'test_add_members_node:80',
            self.py5.get_pool_members(name='test_add_members_pool')
            ['items'][0]['name'])
        self.py5.remove_member_from_pool(target_pool='test_add_members_pool',
                                         member_name='test_add_members_node')
        self.py5.delete_node('test_add_members_node')
        self.py5.delete_pool('test_add_members_pool')

    def test_remove_from_pool(self):
        self.py5.create_pool(name='test_remove_members_pool')
        self.py5.create_node(name='test_remove_members_node',
                             address='123.123.123.123')
        self.py5.add_members_to_pool(
            target_pool='test_remove_members_pool',
            new_members=[{'name': 'test_remove_members_node:80'}])
        self.py5.remove_member_from_pool(
            target_pool='test_remove_members_pool',
            member_name='test_remove_members_node')
        self.assertEqual(
            [],
            self.py5.get_pool_members(
                name='test_remove_members_pool')['items'])
        self.py5.delete_node('test_remove_members_node')
        self.py5.delete_pool('test_remove_members_pool')
