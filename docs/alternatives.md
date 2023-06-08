# Alternatives to AWSWL

AWSWL is one solution to the problem of controlling access to AWS resources with changing IP addresses.

## Systems Manager Session Manager

AWS has a feature, [Session Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html), within AWS Systems Manager that can allow you to connect, using your AWS credentials, to private resources in your VPC. In particular, this can allow you to make an SSH connection (or an SSH-like connection) to an instance that isn't public.

## AWS Site-to-Site VPN

If you're working from an office or a set of offices and you have good networking equipment and networking personnel, it's more common to use an [AWS site-to-site VPN](https://docs.aws.amazon.com/vpn/index.html), allowing you to connect the internal network of your office(s) to the internal network of your VPC(s).

In a more complex environment, you might also include something like a Transit Gateway.

## Other VPNs

Some people prefer different VPN solutions and install OpenVPN appliances or a custom VPN on a Linux EC2 instance. This is not a VPN recommendation guide, but it's worth pointing out that there are other VPN choices available.

## etc

This is not an exhaustive list -- there are lots of other choices: Teleport, Direct Connect and probably a bunch of choices I haven't considered.

If you feel strongly about an alternative and you want to add it to the documentation, feel free to raise a PR.
