# Usage

## Common Cases

These are the most common operations.  I'm going to use made-up ip addresses in these listings, so don't read too deeply into the specifics.

### Listing IP Addresses in the Security Group

Often, I'll want to check if my current ip address is in a security group:

```shell
❯ awswl --sgid sg-0123456abc --list
The following CIDR blocks are authorized for SSH:
- 192.168.0.0/16                    (Bastion Host)
- 172.16.0.0/21
- 8.8.8.8/32                        (Quad 8)
```

Any descriptions that have been added to AWS metadata will appear as well.

These IP addresses are made up, but if my current external ip address were listed (or if my current external ip address is included in a larger block in this list), it should be marked with `(current)`.  This is what it would look like if I were in the list:

```shell
❯ awswl --sg-name "mycorp-prod-bastion" --list
The following CIDR blocks are authorized for SSH:
- 192.168.0.0/16                    (Bastion Host)
- 172.16.0.0/21
- 8.8.8.8/32                        (Quad 8)
- 1.2.3.4/32                        (current)
```

### Adding My Current External IP

If I want to give myself access to a security group, I could `--add-current`:

```shell
❯ awswl --sgid sg-0123456abc add-current
Added current external IP address as a CIDR block (1.2.3.4/32) to allowlist w/o description.
```

If I want to make sure that my addition gets a description, I can add an automatic description:
```shell
❯ awswl --sgid sg-0123456abc add-current --auto-desc
Added current external IP address as a CIDR block (1.2.3.4/32) to allowlist w/ description 'geoffrey - 2023-09-01'.
```

Or one that I specify myself:
```shell
❯ awswl --sgid sg-0123456abc add-current --desc 'Bastion Host'
Added current external IP address as a CIDR block (1.2.3.4/32) to allowlist w/ description 'Bastion Host'.
```


### Removing My Current External IP
 
If I'm working in an environment temporarily, I might want to revoke access as soon as I'm done, using `--remove-current`

```shell
❯ awswl --sg-name "myorg-jump-host" remove-current
Removed current external IP address as a CIDR block (4.3.2.1/32) from allowlist.
```

### Adding or Removing a Custom CIDR

Although I usually want my current external ip address, there are certainly cases where you might want to allow-list a custom CIDR block:

```shell
❯ awswl --sgid sg-0123456abc add 8.8.8.8/28
Added specified CIDR block (8.8.8.0/28) to allowlist w/o description.

❯ awswl --sg-name "*beta-extern*" --remove 8.8.8.8/28
Removed 8.8.8.0/28 from allowlist.
```

You can use `--auto-desc` or `--desc` when adding custom CIDRs as well if you want to make sure the security group rules have descriptions.  

## Updating an Existing CIDR

If I've already added a CIDR with a description, I can update it to a new value. This is typically useful if your IP address changes from time to time (often true for home connections) or if you work from more than one location but you want to make sure that only the location you're currently working from is on the allowlist.

I can do this by specifying the CIDR:
```shell
❯ awswl --sg-name "codiform-bastion" update "8.8.8.8/32" --desc "Geoffrey Home"
Using security group codiform-bastion (sg-00abcdef9234).

Removed old value (7.7.7.7/32) from allowlist.
Added new value (8.8.8.8/32) to allowlist w/ description 'Geoffrey Home'```

Or using my current IP Address:
```shell
❯ awswl --sg-name "codiform-bastion" update-current --desc "Codiform HQ"
Using security group codiform-bastion (sg-00abcdef9234).

Removed old value (8.8.8.8/32) from allowlist.
Added new value (7.7.7.7/32) to allowlist w/ description 'Codiform HQ'
```

Since the goal here is to update a fixed description with a new value, `--desc` is required and `--auto-desc` is not an option.

If the description matches more than one rule, the update will fail, since it's not likely that you wanted multiple rules with the same new value:
```shell
❯ poetry run awswl --sg-name "codiform-bastion" update-current --desc "GitHub Runner"
Using security group codiform-bastion (sg-00abcdef9234).

Update failed: found more than one CIDR matching description.
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
