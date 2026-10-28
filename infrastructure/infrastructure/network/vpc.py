
from aws_cdk import aws_ec2 as ec2
from constructs import Construct

from .subnet_config import get_subnet_configuration


def create_vpc(
    scope: Construct,
    construct_id: str,
) -> ec2.Vpc:

    return ec2.Vpc(
        scope,
        construct_id,
        vpc_name="migration-vpc",
        ip_addresses=ec2.IpAddresses.cidr("10.20.0.0/16"),
        max_azs=2,
        nat_gateways=2,
        subnet_configuration=get_subnet_configuration(),
    )
