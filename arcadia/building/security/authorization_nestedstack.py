from aws_cdk import (
    # Duration,
    aws_s3 as s3, aws_iam as iam,
    NestedStack, RemovalPolicy, CfnOutput, )
from constructs import Construct


class AuthorizationNestedStack(NestedStack):

    def __init__(self, scope: Construct, construct_id: str,
                 removal_policy: RemovalPolicy = RemovalPolicy.RETAIN,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # below role is assumed by ec2 instance
        role = iam.Role(self, "Squad44Role", role_name="Squad44Role",
                        assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))
        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name(
            "AmazonSSMManagedInstanceCore"))
        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name(
            "EC2InstanceProfileForImageBuilder"))
        role.apply_removal_policy(removal_policy)

        # create an instance profile to attach the role
        self.instance_profile = iam.InstanceProfile(self,
                                                    "Squad44InstanceProfile",
                                                    instance_profile_name="Squad44InstanceProfile",
                                                    role=role)
        self.instance_profile.apply_removal_policy(removal_policy)
