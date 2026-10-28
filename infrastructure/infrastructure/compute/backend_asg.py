
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_autoscaling as autoscaling
from constructs import Construct


class BackendAutoScalingGroup(Construct):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.IVpc,
        backend_security_group: ec2.ISecurityGroup,
    ) -> None:
        super().__init__(scope, construct_id)

        # Temporary Node.js application for infrastructure testing.
        # GitHub Actions will deploy the real application later.
        user_data = ec2.UserData.for_linux()

        user_data.add_commands(
            "dnf install -y nodejs",
            "mkdir -p /opt/backend",
            "cat > /opt/backend/server.js <<'EOF'",
            "const http = require('http');",
            "const server = http.createServer((req, res) => {",
            "  if (req.url === '/health') {",
            "    res.writeHead(200, {'Content-Type': 'application/json'});",
            "    res.end(JSON.stringify({status: 'healthy'}));",
            "    return;",
            "  }",
            "  res.writeHead(200, {'Content-Type': 'application/json'});",
            "  res.end(JSON.stringify({message: 'Backend is running'}));",
            "});",
            "server.listen(8080, '0.0.0.0');",
            "EOF",
            "cat > /etc/systemd/system/backend.service <<'EOF'",
            "[Unit]",
            "Description=Node.js Backend Application",
            "After=network.target",
            "",
            "[Service]",
            "Type=simple",
            "WorkingDirectory=/opt/backend",
            "ExecStart=/usr/bin/node /opt/backend/server.js",
            "Restart=always",
            "RestartSec=5",
            "",
            "[Install]",
            "WantedBy=multi-user.target",
            "EOF",
            "systemctl daemon-reload",
            "systemctl enable --now backend.service",
        )

        self.asg = autoscaling.AutoScalingGroup(
            self,
            "BackendASG",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_group_name="backend",
            ),
            instance_type=ec2.InstanceType("m7i.xlarge"),
            machine_image=ec2.MachineImage.latest_amazon_linux2023(),
            security_group=backend_security_group,
            user_data=user_data,
            min_capacity=1,
            desired_capacity=1,
            max_capacity=2,
        )

        # Enable administration through AWS Systems Manager.
        self.asg.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "AmazonSSMManagedInstanceCore"
            )
        )

        # Scale based on average CPU utilization.
        self.asg.scale_on_cpu_utilization(
            "BackendCpuTargetTracking",
            target_utilization_percent=75,
        )
