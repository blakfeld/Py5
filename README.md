# Py5 #

Py5 is a fairly small wrapper for F5's iControl REST API. It consists of a
single class that contains various methods for performing various actions
against an F5.

Requires your F5 be at least version 11.5 and that you have a local account
registered on the actual device.

I highly recommend checking out the [official docs](https://devcentral.f5.com/d/icontrol-rest-user-guide-version-1150)
if you're wondering what all you have access to.

## Installation ##

Just run setup.py!

    python setup.py install

## Configuration ##

To use py5 as a module, you'll need to have the fqdn/IP address of the
F5 server, a username/password, and optionally you can choose whether or not
to validate SSL certs.

All functionality lies in the iControlREST class:

    py5 = py5.iControlREST(server='123.123.123.123',
                           username='username',
                           password='password',
                           verify=True)

To use py5-cli there are a few options for configuration. You can configure
global configuration using 'py5.conf' in the this directory. You can
configure per user configuration by placing '.py5' in your home directory.
You can also just specify on the command line at runtime.

The config file should be a yaml file structured like:

    py5:
        server: 'xxx.xxx.xxx.xxx'
        username: 'username'
        password: 'password'
        verify_ssl: True

However, if you choose not to specify your password in plaintext (and who
could blame you) you will be prompted for it.

## CLI Usage ##

At any time you can see the full list of commands by typing:

    py5-cli.py --h

Here are some common operations

### List All Pools ###

    py5-cli.py --list-pools

    py5.get_all_pools()

### List All Nodes ###

    py5-cli.py --list-nodes

    py5.get_all_nodes()

### Add Node to Pool ###

**Note:** You must include the port in the node name (NODE_NAME:PORT)

    py5-cli.py --add-node-to-pool NODE_NAME:PORT POOL_NAME

    py5.add_members_to_pool(target_pool='POOL_NAME',
                            new_members=[{'name': 'NODE_NAME:PORT'}])

### Remove Node from Pool ###

**Note:** You must include the port in the node name (NODE_NAME:PORT)

    py5-cli.py --remove-node-from-pool NODE_NAME:PORT POOL_NAME

    py5.remove_members_from_pool(target_pool='POOL_NAME',
                                 member_name='NODE_NAME')

### Disable Node ###

    py5-cli.py --disable-node NODE_NAME

    py5.disable_node(name='NODE_NAME')

### Enable Node ###

    py5-cli.py --enable-node NODE_NAME


    py5.enable_node(name='NODE_NAME')

### Disable Node in Pool ###

**Note:** You must include the port in the node name (NODE_NAME:PORT)

    py5-cli.py --disable-pool-member POOL_NAME NODE_NAME:PORT

    py5.disable_pool_member(name='POOL_NAME', member_name='NODE_NAME:PORT')

### Enable Node in Pool ###

**Note:** You must include the port in the node name (NODE_NAME:PORT)

    py5-cli.py --enable-pool-member POOL_NAME NODE_NAME:PORT

    py5.enable_pool_member(name='POOL_NAME', member_name='NODE_NAME:PORT')
