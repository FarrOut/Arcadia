from aws_cdk import (

    Duration,
    NestedStack,
    aws_ec2 as ec2,
    aws_logs as logs, CfnOutput, RemovalPolicy,
)
from aws_cdk.aws_iam import Role, ServicePrincipal, ManagedPolicy, PolicyStatement
from aws_cdk.aws_s3 import Bucket
from aws_cdk.aws_ec2 import InitFile
from constructs import Construct


class Instances(NestedStack):

    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc, security_group: ec2.SecurityGroup,
                 machine_image: ec2.IMachineImage,
                 key_name: str, debug_mode: bool = False, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        role = Role(self, "MyInstanceRole",
                    assumed_by=ServicePrincipal("ec2.amazonaws.com")
                    )
        # role.add_managed_policy(ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess"))
        role.add_managed_policy(ManagedPolicy.from_aws_managed_policy_name(
            "AWSCloudFormationFullAccess"))
        role.add_to_policy(PolicyStatement(
            resources=["*"],
            actions=["ssm:UpdateInstanceInformation"]
        ))
        role.apply_removal_policy(RemovalPolicy.DESTROY)

        # =====================
        # STORAGE
        # =====================

        # =====================
        # COMPUTING
        # =====================

        # CentOS
        # centos_bootstrapping = ec2.UserData.for_linux()
        # centos_bootstrapping.add_commands()
        # amalin_image = ec2.MachineImage.latest_amazon_linux(user_data=centos_bootstrapping)

        # Ubuntu
        ubuntu_bootstrapping = ec2.UserData.for_linux()

        # # https://aws.amazon.com/premiumsupport/knowledge-center/install-cloudformation-scripts/
        # # https://gist.github.com/mmasko/66d34b651642525c63cd39251e0c2a8b#gistcomment-3931793
        ubuntu_bootstrapping.add_commands(
            'sudo apt-get -y update',
            'sudo apt-get -y upgrade',
            'sudo apt-get -y install python3 python3-pip unzip',

            # Download Cloudformation Helper Scripts
            'mkdir -p /opt/aws/bin/',

            'pip3 install https://s3.amazonaws.com/cloudformation-examples/aws-cfn-bootstrap-py3-latest.tar.gz',
            'ln -s /usr/local/init/ubuntu/cfn-hup /etc/init.d/cfn-hup',
            'ln -s /usr/local/bin/cfn-signal /opt/aws/bin/'
            'ln -s /usr/local/bin/cfn-init /opt/aws/bin/'
            # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-helper-scripts-reference.html
            # 'wget https://s3.amazonaws.com/cloudformation-examples/aws-cfn-bootstrap-py3-latest.zip',
            # 'python3 -m easy_install --script-dir /opt/aws/bin aws-cfn-bootstrap-py3-latest.zip',
        )

        if debug_mode:
            CfnOutput(self, 'MachineImageOutput',
                      value=str(machine_image.get_image(self).image_id),
                      description='MachineImageId',
                      )
            # CfnOutput(self, 'MachineImageUserDataOutput',
            #           value=str(image.get_image(self).user_data.render()),
            #           description='MachineImage UserData',
            #           )

        # View instance Logs in the Console
        # https: // docs.aws.amazon.com / systems - manager / latest / userguide / monitoring - cloudwatch - agent.html
        # https: // docs.aws.amazon.com / AmazonCloudWatch / latest / monitoring / Install - CloudWatch - Agent - New - Instances - CloudFormation.html
        # https://aws.amazon.com/blogs/devops/view-cloudformation-logs-in-the-console/
        # https://s3.amazonaws.com/cloudformation-templates-us-east-1/CloudWatch_Logs.template
        instance_log_group = logs.LogGroup.from_log_group_name(self, 'InstanceLogGroup',
                                                               log_group_name='InstanceLogGroup')

        working_dir = '/home/ubuntu/'
        handle = ec2.InitServiceRestartHandle()
        # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-init.html
        init_ubuntu = ec2.CloudFormationInit.from_config_sets(
            config_sets={
                # Applies the configs below in this order
                "packaging": [],
                "logging": ['install_cw_agent'],
                "testing": [],
                "sysadmin": ['awscli', "networking"],
                'connectivity': ['install_mosh'],
            },
            configs={

                'awscli': ec2.InitConfig([
                    # https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
                    ec2.InitFile.from_url(
                        file_name=working_dir + 'awscliv2.zip',
                        url="https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip",
                    ),
                    ec2.InitPackage.apt(
                        package_name='unzip',
                    ),
                    ec2.InitCommand.shell_command(
                        'unzip awscliv2.zip',
                        cwd=working_dir,
                    ),
                    ec2.InitCommand.shell_command(
                        "sudo ./aws/install",
                        cwd=working_dir,
                    ),
                ]),

                'install_mosh': ec2.InitConfig([
                    ec2.InitPackage.apt(
                        package_name='mosh',
                    ),
                    ec2.InitCommand.shell_command(
                        shell_command="sudo ufw allow 60000:61000/udp",
                        cwd=working_dir),
                ]),

                'install_cw_agent': ec2.InitConfig([

                    # Manually create or edit the CloudWatch agent configuration file
                    # https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Agent-Configuration-File-Details.html

                    # Installing and running the CloudWatch agent on your servers
                    # https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/install-CloudWatch-Agent-commandline-fleet.html

                    ec2.InitFile.from_url(
                        file_name=working_dir + '/amazon-cloudwatch-agent.deb',
                        url='https://s3.amazonaws.com/amazoncloudwatch-agent/debian/amd64/latest/amazon-cloudwatch'
                            '-agent.deb'),
                    ec2.InitCommand.shell_command(
                        shell_command='dpkg -i -E ./amazon-cloudwatch-agent.deb',
                        cwd=working_dir)

                    # TODO Design config file and start CloudWatch agent service
                    # Installing the CloudWatch agent on new instances using AWS CloudFormation
                    # https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Install-CloudWatch-Agent-New-Instances-CloudFormation.html
                ]),
                'networking': ec2.InitConfig([
                    ec2.InitPackage.apt(
                        package_name='net-tools',
                    ),
                ])
            }
        )

        init = init_ubuntu
        instance = ec2.Instance(self, "Instance",
                                vpc=vpc,
                                instance_type=ec2.InstanceType.of(
                                    ec2.InstanceClass.C5A, ec2.InstanceSize.XLARGE4),
                                machine_image=machine_image,
                                key_name=key_name,
                                security_group=security_group,
                                role=role,
                                init=init,
                                user_data_causes_replacement=True,

                                # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ec2/ApplyCloudFormationInitOptions.html
                                init_options=ec2.ApplyCloudFormationInitOptions(
                                    # Optional, which configsets to activate (['default'] by default)
                                    config_sets=["connectivity", 'sysadmin'],

                                    # Don’t fail the instance creation when cfn-init fails. You can use this to
                                    # prevent CloudFormation from rolling back when instances fail to start up,
                                    # to help in debugging. Default: false
                                    ignore_failures=debug_mode,

                                    # Force instance replacement by embedding a config fingerprint. If true (the default), a hash of the config will be embedded into the UserData, so that if the config changes, the UserData changes.
                                    embed_fingerprint=True,

                                    # Optional, how long the installation is expected to take (5 minutes by default)
                                    timeout=Duration.minutes(5),

                                    # Optional, whether to include the --url argument when running cfn-init and cfn-signal commands (false by default)
                                    include_url=False,

                                    # Optional, whether to include the --role argument when running cfn-init and cfn-signal commands (false by default)
                                    include_role=False
                                ),
                                vpc_subnets=ec2.SubnetSelection(
                                    subnet_type=ec2.SubnetType.PUBLIC),
                                )

        # TODO convert to Spot instances
        #
        # Launching EC2 Spot Instances via EC2 Auto Scaling group
        # https://ec2spotworkshops.com/launching_ec2_spot_instances/asg.html

        # asg = autoscaling.AutoScalingGroup(self, "ASG",
        #                                    vpc=vpc,
        #                                    instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3,
        #                                                                      ec2.InstanceSize.LARGE),
        #                                    machine_image=image,
        #                                    security_group=outer_perimeter_security_group,
        #                                    associate_public_ip_address=True,
        #                                    allow_all_outbound=True,
        #                                    role=role,
        #                                    key_name=key_name,
        #                                    init=init,
        #                                    # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ec2/ApplyCloudFormationInitOptions.html
        #                                    init_options=autoscaling.ApplyCloudFormationInitOptions(
        #                                        # Optional, which configsets to activate (['default'] by default)
        #                                        config_sets=["connectivity"],
        #
        #                                        # Don’t fail the instance creation when cfn-init fails. You can use this to
        #                                        # prevent CloudFormation from rolling back when instances fail to start up,
        #                                        # to help in debugging. Default: false
        #                                        ignore_failures=debug_mode,
        #
        #                                        # Optional, whether to include the --url argument when running cfn-init and cfn-signal commands (false by default)
        #                                        include_url=False,
        #
        #                                        # Optional, whether to include the --role argument when running cfn-init and cfn-signal commands (false by default)
        #                                        include_role=False
        #                                    ),
        #                                    signals=autoscaling.Signals.wait_for_all(
        #                                        timeout=cdk.Duration.minutes(2)
        #                                    ),
        #                                    update_policy=autoscaling.UpdatePolicy.replacing_update(),
        #                                    # Be aware this will reset the size of your AutoScalingGroup on every deployment.
        #                                    # See https://github.com/aws/aws-cdk/issues/5215
        #                                    desired_capacity=1,
        #                                    min_capacity=0,
        #                                    max_capacity=5,
        #                                    vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
        #                                    )

        # TODO Scale out or in based on time.
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_autoscaling/AutoScalingGroup.html#aws_cdk.aws_autoscaling.AutoScalingGroup.scale_on_schedule
        # To have a warm pool ready for the day ahead
        self.instance_public_name = instance.instance_public_dns_name
        CfnOutput(self, 'InstancePublicDNSname',
                  value=self.instance_public_name,
                  description='Publicly-routable DNS name for this instance.',
                  )

        user = 'ubuntu'
        self.ssh_command = 'ssh' + ' -v' + ' -i ' + key_name + \
            '.pem ' + user + '@' + self.instance_public_name
        CfnOutput(self, 'InstanceSSHcommand',
                  value=self.ssh_command,
                  description='Command to SSH into instance.',
                  )

        self.mosh_command = f"mosh --ssh=\"ssh -i {key_name}.pem\" {user}@{self.instance_public_name}"
        self.mobaxterm_mosh_command = \
            f"mobaxterm -newtab \"mosh --ssh=\\\"ssh -i {key_name}.pem\\\"\" {user}@{self.instance_public_name}"
