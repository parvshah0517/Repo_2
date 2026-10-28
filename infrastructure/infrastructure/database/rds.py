
from aws_cdk import Duration, RemovalPolicy
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_rds as rds
from constructs import Construct


class RdsDatabaseConstruct(Construct):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.IVpc,
        database_security_group: ec2.ISecurityGroup,
    ) -> None:
        super().__init__(scope, construct_id)

        # Create a managed MySQL database.
        self.database = rds.DatabaseInstance(
            self,
            "MigrationMySQLDatabase",

            # Database engine
            engine=rds.DatabaseInstanceEngine.mysql(
                version=rds.MysqlEngineVersion.VER_8_0_39
            ),

            # Initial sizing candidate.
            # Validate against the existing DB workload before production.
            instance_type=ec2.InstanceType("m7i.2xlarge"),

            # Network configuration
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_group_name="database",
            ),
            security_groups=[database_security_group],
            port=3306,
            publicly_accessible=False,

            # High availability
            multi_az=True,

            # Storage
            allocated_storage=100,
            max_allocated_storage=200,
            storage_encrypted=True,

            # Credentials are generated and stored in Secrets Manager.
            credentials=rds.Credentials.from_generated_secret(
                "dbadmin",
                secret_name="migration/rds/master",
            ),

            # Initial database name
            database_name="applicationdb",

            # Backup and maintenance
            backup_retention=Duration.days(7),
            auto_minor_version_upgrade=True,

            # Protect against accidental deletion
            deletion_protection=True,
            removal_policy=RemovalPolicy.RETAIN,
        )
