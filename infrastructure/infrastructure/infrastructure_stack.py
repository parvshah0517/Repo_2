
from aws_cdk import Stack, CfnOutput
from constructs import Construct

from .network.vpc import create_vpc
from .security.security_groups import SecurityGroups
from .load_balancer.alb import ApplicationLoadBalancerConstruct
from .compute.web_asg import WebAutoScalingGroup
from .compute.backend_asg import BackendAutoScalingGroup
from .database.rds import RdsDatabaseConstruct


class InfrastructureStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. Create the network
        self.vpc = create_vpc(
            self,
            "MigrationVpc",
        )

        # 2. Create security groups
        self.security_groups = SecurityGroups(
            self,
            "SecurityGroups",
            vpc=self.vpc,
        )

        # 3. Create the Application Load Balancer
        self.load_balancer = ApplicationLoadBalancerConstruct(
            self,
            "LoadBalancer",
            vpc=self.vpc,
            alb_security_group=self.security_groups.alb,
        )

        # 4. Create the backend Auto Scaling Group
        self.backend_tier = BackendAutoScalingGroup(
            self,
            "BackendTier",
            vpc=self.vpc,
            backend_security_group=self.security_groups.backend,
        )

        # 5. Create the RDS database
        self.rds_database = RdsDatabaseConstruct(
            self,
            "RdsDatabase",
            vpc=self.vpc,
            database_security_group=self.security_groups.database,
        )

        # 6. Grant the backend access to database credentials
        self.rds_database.database.secret.grant_read(
            self.backend_tier.asg.role
        )

        # 7. Export database connection details
        CfnOutput(
            self,
            "DatabaseEndpoint",
            value=self.rds_database.database.db_instance_endpoint_address,
            description="RDS MySQL endpoint",
        )

        CfnOutput(
            self,
            "DatabasePort",
            value=self.rds_database.database.db_instance_endpoint_port,
            description="RDS MySQL port",
        )

        CfnOutput(
            self,
            "DatabaseSecretArn",
            value=self.rds_database.database.secret.secret_arn,
            description="Secrets Manager ARN for database credentials",
        )
