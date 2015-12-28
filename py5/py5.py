"""
Wrapper to interact with an F5 Load Balancer. Documentation about the
    iControl REST API can be found at:
        https://devcentral.f5.com/d/icontrol-rest-user-guide-version-1150

**NOTE:** You must have a local *Administrator* account on the f5
    to have access to the REST API.

Author: Corwin Brown
"""

import json
import requests


class iControlREST(object):
    def __init__(self,
                 server,
                 username,
                 password,
                 verify=True,
                 debug=False):
        """
        Constructor

        Parameters:
            server -- IP address/hostname of F5 (omit "http" and "/mgmt/tm")
            username -- Username to log into the F5
            password -- Password for Username
            expandSubcollections -- Show data inside all subcollections
            verify -- Specify if insecure connections are allowed.
            self.debug -- Toggle bombing out on error
        """

        self.url_base = 'https://{0}/mgmt/tm'.format(server)
        self.debug = debug

        # Build requests object
        self.icontrol = requests.session()
        self.icontrol.auth = (username, password)
        self.icontrol.verify = verify
        self.icontrol.headers.update({'Content-Type': 'application/json'})

    """
    Pool Methods
    """

    def get_all_pools(self):
        resp = self.icontrol.get('{0}/ltm/pool/'.format(self.url_base))
        if not self.debug:
            resp.raise_for_status()

        return resp.json()

    def get_all_pools_in_partition(self, partition='Common'):
        resp = self.icontrol.get('{0}/ltm/pool?$filter=partition eq {1}'
                                 .format(self.url_base,
                                         partition))
        if not self.debug:
            resp.raise_for_status()

        return resp.json()

    def get_pool(self, name, partition='Common'):
        resp = self.icontrol.get('{0}/ltm/pool/~{1}~{2}/'
                                 .format(self.url_base,
                                         partition,
                                         name))
        if not self.debug:
            resp.raise_for_status()

        return resp.json()

    def create_pool(self, **kwargs):
        """
        For full list of attributes check F5's documentation:
            https://devcentral.f5.com/d/icontrol-rest-user-guide-version-1150

        Sample Payload:
            {
                'name': 'Pool Name',
                'partition': 'Common',
                'members': [
                    {
                        'name': 'Node 1',
                        'description': 'First Added'
                    },
                        'name': 'Node 2',
                        'description': 'Second Added'
                    }
                ]
            }

        Sample call:
            create_pool(name='Pool Name',
                        partition='Common',
                        members=[{'name': 'Node 1', 'description': 'First'}])
        """

        resp = self.icontrol.post('{0}/ltm/pool'.format(self.url_base),
                                  data=json.dumps(kwargs))
        if not self.debug:
            resp.raise_for_status()

        return resp.json()

    def modify_pool(self, name, partition='Common', **kwargs):
        """
        For full list of attributes check F5's documentation:
            https://devcentral.f5.com/d/icontrol-rest-user-guide-version-1150

        Sample Payload:
            {
                'partition': 'New_Partition'
            }

        Sample call:
            modify_pool(name='Pool Name', session='user-disabled')
        """

        resp = self.icontrol.put('{0}/ltm/pool/~{1}~{2}'.format(self.url_base,
                                                                partition,
                                                                name),
                                 data=json.dumps(kwargs))
        if not self.debug:
            resp.raise_for_status()

        return resp.json()

    def delete_pool(self, name, partition='Common'):
        # Ensure exists
        pool = self.get_pool(name=name, partition=partition)
        if 'code' not in pool and 'errorStack' not in pool:
            resp = self.icontrol.delete('{0}/ltm/pool/~{1}~{2}'
                                        .format(self.url_base,
                                                partition,
                                                name))
            if not self.debug:
                resp.raise_for_status()
            # Ensure no longer exists
            pool = self.get_pool(name)
            if 'code' in pool and pool['code'] == 404:
                return {}

            return resp.json()

        return pool

    def get_pool_members(self, name, partition='Common'):
        resp = self.icontrol.get('{0}/ltm/pool/~{1}~{2}/members/'
                                 .format(self.url_base,
                                         partition,
                                         name))
        if not self.debug:
            resp.raise_for_status()

        return resp.json()

    def get_pool_member_state(self,
                              name,
                              member_name,
                              partition='Common'):

        resp = self.icontrol.get('{0}/ltm/pool/~{1}~{2}/members/~{1}~{3}/'
                                 .format(self.url_base,
                                         partition,
                                         name,
                                         member_name))
        if not self.debug:
            resp.raise_for_status()

        return resp.json()

    def get_pool_stats(self, name, partition='Common'):
        resp = self.icontrol.get('{0}/ltm/pool/~{1}~{2}/stats'
                                 .format(self.url_base,
                                         partition,
                                         name))
        if not self.debug:
            resp.raise_for_status()

        return resp.json()

    def add_members_to_pool(self,
                            target_pool,
                            new_members,
                            partition='Common'):
        """
        Sample Payload:
            [
                {
                    'name': 'new_member:PORT',
                    'address': 'xxx.xxx.xxx.xxx',
                    'description': 'This is a new member.'
                },
                ...
            ]

        Sample Call:
            add_members_to_pool(target_pool='Pool Name',
                                new_members=[{'name': 'new_member',
                                              'address': 'xxx.xxx.xxx.xxx',
                                              'description': 'New Member!'}])

        NOTE:
            * Member names *MUST* include a port number.
            * new_members must be a list of dictionaries.
        """

        # If we don't include the current members in the request
        #   they'll be overwritten
        current_members = self.get_pool_members(name=target_pool,
                                                partition=partition)
        members = list()
        if current_members['items']:
            members.extend(current_members['items'])

        members.extend(new_members)

        return self.modify_pool(name=target_pool,
                                partition=partition,
                                members=members)

    def remove_member_from_pool(self,
                                target_pool,
                                member_name,
                                partition='Common'):

        current_members = self.get_pool_members(name=target_pool,
                                                partition=partition)

        # Bail if no members
        if 'items' not in current_members or not current_members['items']:
            return {'code': 400, 'message': 'No Members in Pool.'}

        members = current_members['items']
        member_name = member_name.split(':')[0]
        member_index = None
        for i, _ in enumerate(members):
            if _['name'].split(':')[0] == member_name:
                member_index = i
                break

        # Bail if we don't find it.
        if member_index is None:
            return {'code': 400, 'message': 'Member not in Pool.'}

        members.pop(member_index)

        return self.modify_pool(name=target_pool,
                                partition=partition,
                                members=members)

    def modify_member_in_pool(self,
                              name,
                              member_name,
                              partition='Common',
                              **kwargs):
        """
        For full list of attributes check F5's documentation:
            https://devcentral.f5.com/d/icontrol-rest-user-guide-version-1150

        Sample Payload:
            {
                'session': user-disabled
            }

        Sample call:
            modify_pool(name='Pool Name',
                        member_name='member_name',
                        session='user-disabled')
        """

        resp = self.icontrol.put('{0}/ltm/pool/~{1}~{2}/members/{3}'
                                 .format(self.url_base,
                                         partition,
                                         name,
                                         member_name),
                                 data=json.dumps(kwargs))
        if not self.debug:
            resp.raise_for_status()

        return resp.json()

    def disable_pool_member(self, name, member_name, partition='Common'):
        """
        NOTE: member name requires a port.
            NODE_NAME:PORT
        """

        return self.modify_member_in_pool(name=name,
                                          member_name=member_name,
                                          partition=partition,
                                          session='user-disabled')

    def enable_pool_member(self, name, member_name, partition='Common'):
        """
        NOTE: member name requires a port.
            NODE_NAME:PORT
        """

        return self.modify_member_in_pool(name=name,
                                          member_name=member_name,
                                          partition=partition,
                                          session='user-enabled')

    """
    Node Methods
    """

    def get_all_nodes(self):
        resp = self.icontrol.get('{0}/ltm/node'
                                 .format(self.url_base))
        if not self.debug:
            resp.raise_for_status()

        return resp.json()

    def get_all_nodes_in_partition(self, partition='Common'):
        resp = self.icontrol.get('{0}/ltm/node/?$filter=partition eq {1}'
                                 .format(self.url_base,
                                         partition))
        if not self.debug:
            resp.raise_for_status()

        return resp.json()

    def get_node(self, name, partition='Common'):
        resp = self.icontrol.get('{0}/ltm/node/~{1}~{2}'
                                 .format(self.url_base,
                                         partition,
                                         name))
        if not self.debug:
            resp.raise_for_status()

        return resp.json()

    def create_node(self, **kwargs):
        """
        For full list of attributes check F5's documentation:
            https://devcentral.f5.com/d/icontrol-rest-user-guide-version-1150

        Sample Payload:
            {
                'name': 'Test Node',
                'address': 'xxx.xxx.xxx.xxx',
                'description': 'This is a test'
            }

        Sample Call:
            create_node(name='Test Node',
                        address='xxx.xxx.xxx.xxx',
                        description='This is a test')

        **NOTE:** Name and IP Address are required.
        """

        resp = self.icontrol.post('{0}/ltm/node'.format(self.url_base),
                                  data=json.dumps(kwargs))
        if not self.debug:
            resp.raise_for_status()

        return resp.json()

    def modify_node(self, name, partition='Common', **kwargs):
        """
        For full list of attributes check F5's documentation:
            https://devcentral.f5.com/d/icontrol-rest-user-guide-version-1150

        Sample Payload:
            {
                'session': 'user-disabled'
            }

        Sample call:
            modify_node(name='Node Name', session='user-disabled')
        """

        resp = self.icontrol.put('{0}/ltm/node/~{1}~{2}'.format(self.url_base,
                                                                partition,
                                                                name),
                                 data=json.dumps(kwargs))
        if not self.debug:
            resp.raise_for_status()

        return resp.json()

    def delete_node(self, name, partition='Common'):
        # Ensure exists
        node = self.get_node(name=name, partition=partition)
        if 'code' not in node and 'errorStack' not in node:
            resp = self.icontrol.delete('{0}/ltm/node/~{1}~{2}'
                                        .format(self.url_base,
                                                partition,
                                                name))
            if not self.debug:
                resp.raise_for_status()

            node = self.get_node(name)
            if 'code' in node and node['code'] == 404:
                return {}

            return resp.json()

        return node

    def get_node_stats(self, name, partition='Common'):
        resp = self.icontrol.get('{0}/ltm/node/~{1}~{2}/stats'
                                 .format(self.url_base,
                                         partition,
                                         name))
        if not self.debug:
            resp.raise_for_status()

        return resp.json()

    def enable_node(self, name, partition='Common'):
        return self.modify_node(name=name,
                                session='user-enabled',
                                partition=partition)

    def disable_node(self, name, partition='Common'):
        return self.modify_node(name=name,
                                session='user-disabled',
                                partition=partition)

    """
    Partition Methods
    """

    def get_all_partitions(self):
        resp = self.icontrol.get('{0}/sys/folder'.format(self.url_base))

        return resp.json()

    def get_partition(self, name):
        resp = self.icontrol.get('{0}/sys/folder/~{1}'.format(self.url_base,
                                                              name))

        return resp.json()

    def create_partition(self, name):
        """
        It seems all you have to do is specify a name, although
            this could easily be extended to just parse kwargs.

        NOTE: You must specify a full path. So if you want a root
            level folder called "Test", you would have to submit:
                '/Test'
            Or for a nested folder:
                '/Test/Nested_Folder'
        """

        payload = {
            'name': name
        }
        resp = self.icontrol.post('{0}/sys/folder'.format(self.url_base),
                                  data=json.dumps(payload))
        if not self.debug:
            resp.raise_for_status()

        return resp.json()

    def delete_partition(self, name):
        partition = self.get_partition(name)
        if 'code' not in partition and 'errorStack' not in partition:
            resp = self.icontrol.delete('{0}/sys/folder/~{1}'
                                        .format(self.url_base,
                                                name))
            if not self.debug:
                resp.raise_for_status()

            partition = self.get_partition(name)
            if 'code' in partition and partition['code'] == 404:
                return {}

            return resp.json()

        return partition
