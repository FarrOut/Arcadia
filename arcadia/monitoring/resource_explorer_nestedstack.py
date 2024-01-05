from aws_cdk import (
    # Duration,
    aws_s3 as s3, aws_iam as iam, aws_resourcegroups as resourcegroups,
    NestedStack, RemovalPolicy, CfnOutput, )
from constructs import Construct


class ResourceExplorer(NestedStack):

    def __init__(self, scope: Construct, construct_id: str,
                 removal_policy: RemovalPolicy = RemovalPolicy.RETAIN,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        group = resourcegroups.CfnGroup(self, "Squad44CfnGroup",
                                        name="squad44-dedicated-server",

                                        description="All resources belonging to Squad44 Dedicated Server",
                                        resource_query=resourcegroups.CfnGroup.ResourceQueryProperty(
                                            query=resourcegroups.CfnGroup.QueryProperty(
                                                resource_type_filters=[
                                                    "AWS::AllSupported"],
                                                tag_filters=[resourcegroups.CfnGroup.TagFilterProperty(
                                                    key="PropertyOf",
                                                    values=[
                                                        "squad44-dedicated-server"]
                                                )]
                                            ),
                                            type="TAG_FILTERS_1_0",
                                        ))
        group.apply_removal_policy(removal_policy)

        CfnOutput(self, "Squad44DedicatedServerGroupArn",
                  value=group.attr_arn, export_name="Squad44DedicatedServerGroupArn")
        CfnOutput(self, "Squad44DedicatedServerGroupName", value=group.name,
                  description="Squad44 Dedicated Server Group Name", export_name="Squad44DedicatedServerGroupName")
        CfnOutput(self, "Squad44DedicatedServerGroupDescription",
                  value=group.description,)
