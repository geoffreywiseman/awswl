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

## Usage ⌨

If you want usage help at the command line, try:

```bash
awswl --help
```

There's more detailed usage documentation in the documentation, which you can read on [GitHub](docs/usage.md) or [readthedocs](https://awswl.readthedocs.io/en/latest/usage/).


## Environment

All of these require you to have AWS credentials set up in advance, stored in
``~/.aws/credentials``, and if you need to use a profile, you can configure it with
``AWS_PROFILE``. If you want to identify the security group using a command-line variable so that
you don't have to put it into each command invocation, you can put it in ``AWSWL_SGID``.
