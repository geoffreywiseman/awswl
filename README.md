# AWS Allowlist

[![ci](https://github.com/geoffreywiseman/awswl/actions/workflows/ci.yml/badge.svg)](https://github.com/geoffreywiseman/awswl/actions/workflows/ci.yml)
[![Downloads](https://static.pepy.tech/badge/awswl)](https://pepy.tech/project/awswl)
[![Documentation](https://readthedocs.org/projects/awswl/badge/)](https://awswl.readthedocs.io/en/latest/)

A small tool to make it pretty simple to add and remove ip addresses (or CIDR blocks) from an AWS security group. This acts like a sort of oversimplified VPN, where you can quickly give yourself SSH access to a project as you move about from network to network.

This README should have enough information to get started, but you can get more information on:
- recent changes in the [CHANGELOG](CHANGELOG.md)
- documentation on [Read The Docs](https://awswl.readthedocs.io/en/latest/)
- [Alternatives](docs/alternatives.md) to awswl

## Installing 🛠️

This is a python tool, packaged as a python module, so you should be able to just run

```bash
pip install awswl
```    

Of course, if you don't know what a python module is, or you don't have python and pip installed,
you may have additional work ahead of you.

Now that Python2 is largely a relic of the past, I'm focused on supporting Python 3 only. The current CI build is for Python 3.9+.

## Usage

If you want usage help at the command line, try:

```bash
awswl --help
```

You can list the IP address blocks that are authorized, including which ip address is current:

```bash
awswl --list
```

Authorize your current IP Address:

```bash
awswl --add-current
```

Remove authorization for your current IP:

```bash
awswl --remove-current
```

Authorize a manually-specified CIDR block:

```bash
awswl --add 192.168.0.0/24
```

Remove authorization for a manually-specified CIDR block:

```bash
awswl --remove 192.168.0.0/24
```

For each of these commands, you need to tell awswl which security group to use, which you can do
with the ``--sgid`` command-line option or using an environment variable.


## Integration

In order to get your current ip address, ``--list``, ``--add-current`` and ``--remove-current`` will make a request to ``checkip.amazonaws.org``. Because it's another AWS service, seems less likely to be a privacy concern for anyone.

I may [add a switch](https://github.com/geoffreywiseman/awswl/issues/3) to disable that for the anyone who isn't fond of `awswl` making an additional network request, so if that's a concern for you, feel free to vote for it.


## Environment

All of these require you to have AWS credentials set up in advance, stored in
``~/.aws/credentials``, and if you need to use a profile, you can configure it with
``AWS_PROFILE``. If you want to identify the security group using a command-line variable so that
you don't have to put it into each command invocation, you can put it in ``AWSWL_SGID``.
