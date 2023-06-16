# Usage

## Common Cases

These are the most common operations.  I'm going to use made-up ip addresses in these listings, so don't read too deeply into the specifics.

### Listing IP Addresses in the Security Group

Often, I'll want to check if my current ip address is in a security group:

```shell
❯ awswl --sgid sg-0123456abc --list
The following CIDR blocks are authorized for SSH:
- 192.168.0.0/16
- 172.16.0.0/21
- 8.8.8.8/32
```

These IP addresses are made up, but if my current external ip address were listed, it should be marked with `(current)`.  This is what it would look like if I were in the list:

```shell
❯ awswl --sg-name "mycorp-prod-bastion" --list
The following CIDR blocks are authorized for SSH:
- 192.168.0.0/16
- 172.16.0.0/21
- 8.8.8.8/32
- 1.2.3.4/32 (current)
```

### Adding My Current External IP

If I want to give myself access to a security group, I could `--add-current`:

```shell
❯ awswl --sgid sg-0123456abc --add-current
Added current external IP address as a CIDR block (1.2.3.4/32) to allowlist.
```

### Removing My Current External IP
 
If I'm working in an environment temporarily, I might want to revoke access as soon as I'm done, using `--remove-current`

```shell
❯ awswl --sg-name "myorg-jump-host" --remove-current
Removed current external IP address as a CIDR block (4.3.2.1/32) from allowlist.
```
### Adding or Removing a Custom CIDR

Although I usually want my current external ip address, there are certainly cases where you might want to allow-list a custom CIDR block:

```shell
❯ awswl --sgid sg-0123456abc --add 8.8.8.8/28
Added specified CIDR block (8.8.8.0/28) to allowlist.

❯ awswl --sg-name "*beta-extern*" --remove 8.8.8.8/28
Removed specified CIDR block (8.8.8.0/28) from allowlist.
```

## Required Metadata
There's a bunch of required metadata to do this properly.

### AWS Credentials
In order to modify AWS security groups, you need valid AWS credentials for the API calls required.

AWS AllowList is built in Python using boto, which can use an AWS Credentials file or environment variables.

Boto's support for environment variables works fine with `aws-vault` and likely other similar tools. If you've tested `awswl` with a different aws authentication approach, let me know and I can list it here.

There's no attempt to capture or record credentials -- the awswl code doesn't actually interact with the credentials at all, that's all done by `boto`, but do feel free to look over the source to assuage any privacy concerns.

### AWS Region

The desired AWS region can be supplied in an environment variables as well, `AWS_REGION`, although it might also be in your AWS profile or supplied by whatever tool you might use to manage AWS Credentials. 

### Security Group (ID, Name)

In order to modify a security group, AWS AllowList needs to know which security group to modify:

- If you know the security group id, you can specify it as a CLI option, `--sgid`.
- If for a given project you often need a particular security group, you could specify the security group id in an environment variable, `AWSWL_SGID`, and store that in something like [direnv](https://direnv.net).
- If you know the full name of the security group you can specify that as a CLI option, `--sg-name`.
  - Security group name also supports wildcards, so if the full name is difficult but a partial name is easy, you can use something like `--sg-name "*beta-bastion*"`
  - If the wildcards match more than one group, you'll get an error, which will list all the matching security groups with their ids, so you may be able to use that output to specify `--sgid`. 

### SSH Port

If you want to modify a port other than the default SSH port, you can specify the `--ssh-port` CLI option.

### Current IP Address

In order to get your current ip address, ``--list``, ``--add-current`` and ``--remove-current`` will make a request to ``checkip.amazonaws.org``. Because it's another AWS service, seems less likely to be a privacy concern for anyone.

I may [add a switch](https://github.com/geoffreywiseman/awswl/issues/3) to disable that for anyone who isn't fond of `awswl` making an additional network request, so if that's a concern for you, feel free to vote for it.

## Help and Version

If you want to get usage help at the command line, use `--help`:

```shell
❯ awswl --help
usage: awswl [-h] [--list] [--add-current] [--remove-current] [--version] [--sgid SGID] [--sg-name SG_NAME] [--ssh-port SSH_PORT] [--add ADD_BLOCKS] [--remove REMOVE_BLOCKS]

Maintains a list of allowlisted CIDR blocks granted SSH access to AWS via a security group.

options:
  -h, --help            show this help message and exit
  --list                Lists the ip addresses in the security group with SSH access.
  --add-current         Adds the current IP address to the allowlist.
  --remove-current      Remove the current IP address from the allowlist.
  --version             Print the current version of awswl.
  --sgid SGID           The security group to use for SSH access.
  --sg-name SG_NAME     The name of the security group to use (wildcards allowed).
  --ssh-port SSH_PORT   The port used for SSH. By default this is port 22, but some people prefer to access SSH over another port.
  --add ADD_BLOCKS      Adds a manually-specified CIDR block from the allowlist.
  --remove REMOVE_BLOCKS
                        Removes a manually-specified CIDR block from the allowlist.
```

To get the current version, `--version`:

```shell
    ❯ awswl --version
    awswl v1.1.0
```
