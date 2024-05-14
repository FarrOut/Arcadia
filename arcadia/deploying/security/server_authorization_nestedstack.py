from aws_cdk import (
    # Duration,
    aws_s3 as s3,
    aws_iam as iam,
    aws_ec2 as ec2,
    NestedStack,
    RemovalPolicy,
    CfnOutput,
)
from constructs import Construct
from aws_cdk.aws_iam import Role, ServicePrincipal, ManagedPolicy, PolicyStatement


class ServerAuthorization(NestedStack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.IVpc,
        key_name: str,
        whitelisted_peer: ec2.Peer,
        removal_policy: RemovalPolicy = RemovalPolicy.RETAIN,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.role = iam.Role(
            self,
            "ArcadiaServerRole",
            role_name="ArcadiaServerRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
        )
        # role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name(
        #     "AmazonSSMManagedInstanceCore"))
        # role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name(
        #     "EC2InstanceProfileForImageBuilder"))
        self.role.apply_removal_policy(removal_policy)

        # role.add_managed_policy(ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess"))
        self.role.add_managed_policy(
            ManagedPolicy.from_aws_managed_policy_name("AWSCloudFormationFullAccess")
        )
        self.role.add_managed_policy(
            ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")
        )
        self.role.add_to_policy(
            PolicyStatement(resources=["*"], actions=["ssm:UpdateInstanceInformation"])
        )

        # create an instance profile to attach the role
        self.instance_profile = iam.InstanceProfile(
            self,
            "ArcadiaInstanceProfile",
            instance_profile_name="ArcadiaInstanceProfile",
            role=self.role,
        )
        self.instance_profile.apply_removal_policy(removal_policy)

        CfnOutput(
            self,
            "InstanceProfileName",
            value=self.instance_profile.instance_profile_name,
        )
        CfnOutput(
            self,
            "InstanceProfileArn",
            value=self.instance_profile.instance_profile_arn,
        )

        self.security_group = ec2.SecurityGroup(
            self,
            "ArcadiaSecurityGroup",
            allow_all_outbound=True,
            vpc=vpc,
        )

        self.security_group.add_ingress_rule(
            whitelisted_peer,
            ec2.Port.tcp(22),
            "allow ssh access from trusted whitelist",
        )

        self.security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(10027), "game port tcp"
        )
        self.security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.udp(10027), "game port udp"
        )
        self.security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(10037), "query port tcp"
        )
        self.security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.udp(10037), "query port udp"
        )
        self.security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(10038), "query port plus one tcp"
        )
        self.security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.udp(10038), "query port plus one udp"
        )
        self.security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(21114), "rcon tcp"
        )
        self.security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.udp(21114), "rcon udp"
        )
        self.security_group.add_egress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(443),
            "allow SSM Session Manager",
            # TODO replace any_ipv4 with specific service endpoint names
            # Verify that your instance's security group and VPC allow HTTPS (port 443) outbound traffic to the following Systems Manager endpoints :
            #     ssm.<region>.amazonaws.com
            #     ec2messages.<region>.amazonaws.com
            #     ssmmessages.<region>.amazonaws.com
            # If your VPC does not have internet access, you can use VPC endpoints  to allow outbound traffic from your instance.
        )
        CfnOutput(
            self,
            "SecurityGroupId",
            value=self.security_group.security_group_id,
            description="The ID of the Security Group.",
        )

        self.key_pair = ec2.KeyPair.from_key_pair_name(
            self,
            "ArcadiaKeyPair",
            key_name,
        )
        # self.key_pair.apply_removal_policy(removal_policy)

        CfnOutput(
            self,
            "KeyPairName",
            value=self.key_pair.key_pair_name,
            description="The unique name of the key pair.",
        )
        # CfnOutput(
        #     self,
        #     "KeyPairId",
        #     value=self.key_pair.key_pair_id,
        #     description="The unique ID of the key pair.",
        # )
        # CfnOutput(
        #     self,
        #     "KeyPairFingerprint",
        #     value=self.key_pair.key_pair_fingerprint,
        #     description="The fingerprint of the key pair.",
        # )
        # CfnOutput(
        #     self,
        #     "KeyPairPrivateKey",
        #     value=self.key_pair.private_key,
        #     description="The Systems Manager Parameter Store parameter with the pair’s private key material.",
        # )
        # CfnOutput(
        #     self,
        #     "KeyPairFormat",
        #     value=self.key_pair.format,
        #     description="The format of the key pair.",
        # )
