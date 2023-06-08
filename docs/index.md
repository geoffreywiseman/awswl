# AWSWL

A small tool to make it pretty simple to add and remove ip addresses (or CIDR blocks) from an AWS security group. If you have AWS resources on public IPs and you need to control access to those resources (e.g. SSH to an EC2 instance).

This acts like a sort of oversimplified VPN, where you can quickly give yourself SSH access to a project as you move about from network to network.

## Alternatives

In case you're encountering AWSWL without having considered the other options, you might want to consider [the alternatives](alternatives.md) (vpn, session manager, etc).

## Project Name

I named this project when "whitelist" was the most common word for this sort of action. These days, "allowlist" is preferred and is more clear, but renaming the pypy package and cli command will break links, so for now I'm referring to it as "allowlist" even though the repository and cli are named `awswl` instead of `awsal`.
