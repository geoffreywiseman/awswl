AWS Whitelist
=============

.. image:: https://travis-ci.org/geoffreywiseman/awswl.svg?branch=master
    :target: https://travis-ci.org/geoffreywiseman/awswl

A small tool to make it pretty simple to add and remove ip addresses (or CIDR blocks) from an AWS
security group. This acts like a sort of oversimplified VPN, where you can quickly give yourself
SSH access to a project as you move about from network to network.

Better Solutions
----------------

Anyone who knows enough to use a tool like this likely knows that there are better options 
available, from hardware VPNs to software VPNs hosted on an EC2 instance, and so forth. If you
are using this tool and you haven't even considered using something better, this is your chance:
look at the better options, and see if they fit your needs.

Of course, most of those other options require you to get additional hardware or software resources 
involved and might come with costs. I understand, that's why I made a little tool to make do.

Installing
----------

This is a python tool, packaged as a python module, so you should be able to just run

.. code-block:: bash

    $ pip install awswl

Of course, if you don't know what a python module is, or you don't have python and pip installed,
you may have additional work ahead of you.

The `awswl` module should be compatible with both python2 and python3; I have Travis building it
for Python 2.7, 3.4, 3.5, and 3.6.

Usage
-----

If you want usage help at the command line, try:

.. code-block:: bash

    $ awswl --help

You can list the IP address blocks that are authorized:

.. code-block:: bash

    $ awswl --list

Authorize your current IP Address:

.. code-block:: bash

    $ awswl --add-current

Remove authorization for your current IP:

.. code-block:: bash

    $ awswl --remove-current

Authorize a manually-specified CIDR block:

.. code-block:: bash

    $ awswl --add 192.168.0.0/24

Remove authorization for a manually-specified CIDR block:

.. code-block:: bash

    $ awswl --remove 192.168.0.0/24

For each of these commands, you need to tell awswl which security group to use, which you can do
with the ``--sgid`` command-line option or using an environment variable.


Environment
-----------

All of these require you to have AWS credentials set up in advance, stored in ``~/.aws/credentials``,
and if you need to use a profile, you can configure it with ``AWS_PROFILE``. If you want to identify
the security group using a command-line variable so that you don't have to put it into each command
invocation, you can put it in ``AWSWL_SGID``.

