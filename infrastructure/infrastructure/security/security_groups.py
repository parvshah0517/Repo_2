
from aws_cdk import aws_ec2 as ec2
from constructs import Construct


class SecurityGroups(Construct):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.IVpc,
    ) -> None:
        super().__init__(scope, construct_id)

        # ALB security group
        self.alb = ec2.SecurityGroup(
            self,
            "AlbSecurityGroup",
            vpc=vpc,
            description="Controls inbound traffic to the ALB",
            allow_all_outbound=True,
        )

        # Web tier security group
        self.web = ec2.SecurityGroup(
            self,
            "WebSecurityGroup",
            vpc=vpc,
            description="Allows traffic from the ALB",
            allow_all_outbound=True,
        )

        # Backend tier security group
        self.backend = ec2.SecurityGroup(
            self,
            "BackendSecurityGroup",
            vpc=vpc,
            description="Allows API traffic from web servers",
            allow_all_outbound=True,
        )

        # Database security group
        self.database = ec2.SecurityGroup(
            self,
            "DatabaseSecurityGroup",
            vpc=vpc,
            description="Allows MySQL traffic from backend",
            allow_all_outbound=True,
        )

        # Internet -> ALB
        self.alb.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(80),
            "HTTP from internet",
        )

        self.alb.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(443),
            "HTTPS from internet",
        )

        # ALB -> Web tier
        self.web.add_ingress_rule(
            self.alb,
            ec2.Port.tcp(80),
            "Traffic from ALB",
        )

        # Web tier -> Node.js backend
        self.backend.add_ingress_rule(
            self.web,
            ec2.Port.tcp(8080),
            "API traffic from web tier",
        )

        # Backend -> RDS MySQL
        self.database.add_ingress_rule(
            self.backend,
            ec2.Port.tcp(3306),
            "MySQL traffic from backend",
        )
