
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_autoscaling as autoscaling
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from constructs import Construct


class WebAutoScalingGroup(Construct):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.IVpc,
        web_security_group: ec2.ISecurityGroup,
        web_target_group: elbv2.IApplicationTargetGroup,
    ) -> None:
        super().__init__(scope, construct_id)

        # User data installs and starts Nginx
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
            "dnf install -y nginx",
            "systemctl enable nginx",
            "cat > /usr/share/nginx/html/index.html <<'EOF'",
            "<html><body><h1>AWS Migration Web Tier</h1>"
            "<p>Nginx is running successfully.</p></body></html>",
            "EOF",
            "systemctl start nginx",
        )

        # Web Auto Scaling Group
        self.asg = autoscaling.AutoScalingGroup(
            self,
            "WebASG",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_group_name="web",
            ),
            instance_type=ec2.InstanceType("m7i.xlarge"),
            machine_image=ec2.MachineImage.latest_amazon_linux2023(),
            security_group=web_security_group,
            user_data=user_data,
            min_capacity=2,
            desired_capacity=2,
            max_capacity=4,
        )

        # Allow management through Systems Manager
        self.asg.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "AmazonSSMManagedInstanceCore"
            )
        )

        # Register instances with the ALB target group
        self.asg.attach_to_application_target_group(
            web_target_group
        )

        # Scale based on average CPU utilization
        self.asg.scale_on_cpu_utilization(
            "WebCpuTargetTracking",
            target_utilization_percent=75,
        )
         # Create the web tier
        self.web_tier = WebAutoScalingGroup(
            self,
            "WebTier",
            vpc=self.vpc,
            web_security_group=self.security_groups.web,
            web_target_group=(
                self.load_balancer.web_target_group
            ),
        )
