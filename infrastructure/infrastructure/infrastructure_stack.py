
from aws_cdk import Stack
from aws_cdk import aws_ec2 as ec2
from constructs import Construct


class InfrastructureStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Network spanning two Availability Zones
        self.vpc = ec2.Vpc(
            self,
            "MigrationVpc",
            vpc_name="migration-vpc",
            ip_addresses=ec2.IpAddresses.cidr("10.20.0.0/16"),
            max_azs=2,
            nat_gateways=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                ),
                ec2.SubnetConfiguration(
                    name="application",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24,
                ),
                ec2.SubnetConfiguration(
                    name="database",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24,
                ),
            ],
        )
