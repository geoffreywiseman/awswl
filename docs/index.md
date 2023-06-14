# AWSWL

A small tool to make it pretty simple to add and remove ip addresses (or CIDR blocks) from an AWS security group. If you have AWS resources on public IPs and you need to control access to those resources (e.g. SSH to an EC2 instance).

This acts like a sort of oversimplified VPN, where you can quickly give yourself SSH access to a project as you move about from network to network.

## Alternatives

In case you're encountering AWSWL without having considered the other options, you might want to consider [the alternatives](alternatives.md) (vpn, session manager, etc).

## Project Name

I named this project when "whitelist" was the traditional and most common word for this sort of thing. In the interim, there's been some good progress on more inclusive language and now I'd say that "allowlist" is both preferred and more clear.

Renaming the pypy package and cli command will break links, so for now I'm referring to it as "allowlist" even though the repository and cli are named `awswl` instead of `awsal`. 

I may get around to renaming the repository, package and cli -- if you feel strongly about it, drop me a line or file an issue.
