
from aws_cdk import aws_ec2 as ec2


def get_subnet_configuration():
    return [
        ec2.SubnetConfiguration(
            name="public",
            subnet_type=ec2.SubnetType.PUBLIC,
            cidr_mask=24,
        ),
        ec2.SubnetConfiguration(
            name="web",
            subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
            cidr_mask=24,
        ),
        ec2.SubnetConfiguration(
            name="backend",
            subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
            cidr_mask=24,
        ),
        ec2.SubnetConfiguration(
            name="database",
            subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
            cidr_mask=24,
        ),
    ]
