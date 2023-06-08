# AWS Whitelist

[![ci](https://github.com/geoffreywiseman/awswl/actions/workflows/ci.yml/badge.svg)](https://github.com/geoffreywiseman/awswl/actions/workflows/ci.yml)
[![Downloads](https://static.pepy.tech/badge/awswl)](https://pepy.tech/project/awswl)
[![Documentation](https://readthedocs.org/projects/awswl/badge/)](https://awswl.readthedocs.io/en/latest/)

A small tool to make it pretty simple to add and remove ip addresses (or CIDR blocks) from an AWS
security group. This acts like a sort of oversimplified VPN, where you can quickly give yourself
SSH access to a project as you move about from network to network.

You can read about recent changes in the [CHANGELOG](CHANGELOG.md).


## Better Solutions

Anyone who knows enough to use a tool like this likely knows that there are better options 
available, from hardware VPNs to software VPNs hosted on an EC2 instance, and so forth. If you
are using this tool, and you haven't even considered using something better, this is your chance:
look at the better options, and see if they fit your needs.

Of course, most of those other options require you to get additional hardware or software resources 
involved and might come with costs. I understand, that's why I made a little tool to make do.

## Installing

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


## Edge Cases

For simple use cases, ``awswl`` does everything I want it to do, but it's currently a pretty thin
wrapper over the AWS API for authorizing and revoking access via security groups, and as a result
it doesn't do much pre-processing or validating of your requests. There are cases that it doesn't
address. What it's good at is adding and removing simple rules containing a simple CIDR block
and a single port from a security group.

For instance if you remove a block that isn't present, AWS may simply ignore the request, because
the result matches the desired state -- the block isn't authorized. AWSWL doesn't check in advance
that the block is present, so it doesn't add any messaging to explain that the block wasn't removed
because it wasn't present. This is mostly fine, unless you accidentally mistyped, and you failed to
remove a block as a result.

Similarly, if what you've asked for requires a complex modification of a rule, AWSWL won't
compare your request against the authorized rules and make a plan of action that achieves the
desired result. So if there's already a permission that authorizes a set of CIDR blocks, and you
ask to remove one of those CIDR blocks, AWSWL will pass your request on to AWS, which will check
to see if there's a single permission matching your request to revoke, not find it, and not
throw an error, and AWSWL will respond that your action succeeded when in fact, nothing changed,
and the CIDR block you specified may still be authorized.

Similarly, if you ask AWSWL to revoke permissions on a CIDR block that is narrower than the
authorization, you aren't likely to get the desired result. For instance, if you authorize
192.168.0.0/16 and then revoke 192.168.0.0/24 you could argue that the result should be
192.168.1.0/24 all the way through 192.168.255.0/24 authorized and 192.168.0.0/24 not authorized,
but that's definitely not what will happen.

Similarly, it can't modify a permission block that includes a bunch of ports, including SSH.

To be honest, I am not sure that it makes a lot of sense to address those issues so that it can modify
rules like that, but I would prefer it to notice when situations like that are present and warn
about the rules that it didn't modify -- essentially, I'd like it to validate a bit better.
