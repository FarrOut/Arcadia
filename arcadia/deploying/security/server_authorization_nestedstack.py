from aws_cdk import (
    # Duration,
    aws_s3 as s3, aws_iam as iam, aws_ec2 as ec2,
    NestedStack, RemovalPolicy, CfnOutput, )
from constructs import Construct


class ServerAuthorization(NestedStack):

    def __init__(self, scope: Construct, construct_id: str,
                 vpc: ec2.IVpc,
                 whitelisted_peer: ec2.Peer,
                 removal_policy: RemovalPolicy = RemovalPolicy.RETAIN,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        role = iam.Role(self, "Squad44ServerRole", role_name="Squad44ServerRole",
                        assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))
        # role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name(
        #     "AmazonSSMManagedInstanceCore"))
        # role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name(
        #     "EC2InstanceProfileForImageBuilder"))
        role.apply_removal_policy(removal_policy)

        # create an instance profile to attach the role
        self.instance_profile = iam.InstanceProfile(self,
                                                    "Squad44ServerInstanceProfile",
                                                    instance_profile_name="Squad44ServerInstanceProfile",
                                                    role=role)
        self.instance_profile.apply_removal_policy(removal_policy)

        CfnOutput(self, "InstanceProfileName",
                  value=self.instance_profile.instance_profile_name,)
        CfnOutput(self, "InstanceProfileArn",
                  value=self.instance_profile.instance_profile_arn,)

        self.security_group = ec2.SecurityGroup(self, "Squad44ServerSecurityGroup",
                                                allow_all_outbound=True,
                                                vpc=vpc,
                                                )

        self.security_group.add_ingress_rule(whitelisted_peer, ec2.Port.tcp(22),
                                             "allow ssh access from trusted whitelist")

        self.security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(10027), "game port tcp")
        self.security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.udp(10027), "game port udp")
        self.security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(10037), "query port tcp")
        self.security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.udp(10037), "query port udp")
        self.security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(10038), "query port plus one tcp")
        self.security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.udp(10038), "query port plus one udp")
        self.security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(21114), "rcon tcp")
        self.security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.udp(21114), "rcon udp")
        CfnOutput(self, "SecurityGroupId", value=self.security_group.security_group_id,
                  description='The ID of the Security Group.')

        self.key_pair = ec2.KeyPair(self, "KeyPair",
                                    type=ec2.KeyPairType.ED25519,
                                    format=ec2.KeyPairFormat.PEM,
                                    )
        self.key_pair.apply_removal_policy(removal_policy)

        CfnOutput(self, "KeyPairName", value=self.key_pair.key_pair_name,
                  description="The unique name of the key pair.")
        CfnOutput(self, "KeyPairId", value=self.key_pair.key_pair_id,
                  description="The unique ID of the key pair.")
        CfnOutput(self, "KeyPairFingerprint", value=self.key_pair.key_pair_fingerprint,
                  description="The fingerprint of the key pair.")
