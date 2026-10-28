from aws_cdk import Duration
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from constructs import Construct


class ApplicationLoadBalancerConstruct(Construct):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.IVpc,
        alb_security_group: ec2.ISecurityGroup,
    ) -> None:
        super().__init__(scope, construct_id)

        # 1. Internet-facing Application Load Balancer
        self.alb = elbv2.ApplicationLoadBalancer(
            self,
            "ApplicationLoadBalancer",
            vpc=vpc,
            internet_facing=True,
            security_group=alb_security_group,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC,
            ),
        )

        # 2. Target group for web EC2 instances
        self.web_target_group = elbv2.ApplicationTargetGroup(
            self,
            "WebTargetGroup",
            vpc=vpc,
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            target_type=elbv2.TargetType.INSTANCE,
            health_check=elbv2.HealthCheck(
                path="/",
                healthy_http_codes="200-399",
                interval=Duration.seconds(30),
            ),
        )

        # 3. HTTP listener forwards requests to the web target group
        self.http_listener = self.alb.add_listener(
            "HttpListener",
            port=80,
            open=False,
            default_action=elbv2.ListenerAction.forward(
                [self.web_target_group]
            ),
        )
