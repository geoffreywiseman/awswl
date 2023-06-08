## Edge Cases

For simple use cases, ``awswl`` does everything I want it to do, but it's currently a pretty thin wrapper over the AWS API for authorizing and revoking access via security groups, and as a result it doesn't do much pre-processing or validating of your requests. There are cases that it doesn't address. What it's good at is adding and removing simple rules containing a simple CIDR block and a single port from a security group.

For instance if you remove a block that isn't present, AWS may simply ignore the request, because the result matches the desired state -- the block isn't authorized. AWSWL doesn't check in advance that the block is present, so it doesn't add any messaging to explain that the block wasn't removed because it wasn't present. This is mostly fine, unless you accidentally mistyped, and you failed to remove a block as a result.

Similarly, if what you've asked for requires a complex modification of a rule, AWSWL won't compare your request against the authorized rules and make a plan of action that achieves the desired result. So if there's already a permission that authorizes a set of CIDR blocks, and you ask to remove one of those CIDR blocks, AWSWL will pass your request on to AWS, which will check to see if there's a single permission matching your request to revoke, not find it, and not throw an error, and AWSWL will respond that your action succeeded when in fact, nothing changed, and the CIDR block you specified may still be authorized.

If you ask AWSWL to revoke permissions on a CIDR block that is narrower than the authorization, you aren't likely to get the desired result. For instance, if you authorize `192.168.0.0/16` and then revoke `192.168.0.0/24` you could argue that the result should be that `192.168.1.0/24` all the way through `192.168.255.0/24` remain authorized and that `192.168.0.0/24` will be rejected, but that's definitely not what will happen.

AWSLWL also can't modify a permission block that includes a bunch of ports, including SSH.

To be honest, I am not sure that it makes a lot of sense to address those issues so that it can modify rules like that, but I would prefer it to notice when situations like that are present and warn about the rules that it didn't modify -- essentially, I'd like it to validate a bit better.
