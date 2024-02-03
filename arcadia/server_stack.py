from aws_cdk import (
    Duration,
    Stack, RemovalPolicy, CfnOutput, aws_iam as iam,
    aws_ec2 as ec2, aws_autoscaling as autoscaling,
)
from constructs import Construct
from arcadia.deploying.instances_stack import Instances
from arcadia.deploying.networking.vpc_nestedstack import Vpc
from arcadia.deploying.security.server_authorization_nestedstack import ServerAuthorization
from arcadia.storage.build_assets_nestedstack import BuildAssetsNestedStack
from arcadia.storage.s3_nestedstack import S3NestedStack


class Server(Stack):

    def __init__(self, scope: Construct, construct_id: str,
                 #  machine_image: ec2.IMachineImage,
                 whitelisted_peer: ec2.Peer,
                 key_name: str,
                 removal_policy: RemovalPolicy = RemovalPolicy.DESTROY,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = Vpc(self, "Vpc", removal_policy=removal_policy).vpc
        auth_stack = ServerAuthorization(
            self, "ServerAuthorization",
            vpc=vpc,
            whitelisted_peer=whitelisted_peer,
            removal_policy=removal_policy)
        security_group = auth_stack.security_group
        
        # COMPUTING

        machine_image = ec2.MachineImage.lookup(
            name='*tf2*', owners=[str(self.account)],
            filters={'architecture': ['x86_64']},
        )

        # template = ec2.LaunchTemplate(self, "LaunchTemplate",
        #                               machine_image=machine_image,
        #                               security_group=security_group,
        #                               key_pair=key_pair,
        #                               instance_profile=auth_stack.instance_profile,
        #                               ebs_optimized=None,
        #                               block_devices=[ec2.BlockDevice(
        #                                   device_name="/dev/sda1",
        #                                   volume=ec2.BlockDeviceVolume.ebs(
        #                                       volume_size=70,
        #                                       delete_on_termination=True,
        #                                   ),
        #                                   volume_type=ec2.EbsDeviceVolumeType.GP3
        #                               )],
        #                               instance_type=ec2.InstanceType.of(
        #                                   ec2.InstanceClass.R5, ec2.InstanceSize.XLARGE),
        #                               )
        # template.apply_removal_policy(removal_policy)

        # CfnOutput(self, "LaunchTemplateName", value=str(template.launch_template_name),
        #           description='The name of the Launch Template.')
        # CfnOutput(self, "LaunchTemplateId", value=str(template.launch_template_id),
        #           description='The ID of the Launch Template.')
        # CfnOutput(self, "LaunchTemplateDefaultVersionNumber", value=str(
        #     template.default_version_number), description='The default version for the launch template.')

        instances = Instances(self, "Instances", vpc=vpc, key_name=key_name,
                              debug_mode=True, 
                              machine_image=machine_image,
                              security_group=security_group, )

        CfnOutput(self, 'InstancePublicDNSname',
                  value=instances.instance_public_name,
                  description='Publicly-routable DNS name for this instance.',
                  )
        CfnOutput(self, 'InstanceSSHcommand',
                  value=instances.ssh_command,
                  description='Command to SSH into instance.',
                  )
        CfnOutput(self, 'MoshCommand',
                  value=instances.mosh_command,
                  description='Command to SSH into instance over MOSH.',
                  )
        CfnOutput(self, 'MobaXtermMoshCommand',
                  value=instances.mobaxterm_mosh_command,
                  description='Command to create new SSH session over MOSH via MobaXTerm.',
                  )
