from aws_cdk import (
    # Duration,
    aws_s3 as s3, aws_imagebuilder as imagebuilder,
    aws_iam as iam,
    NestedStack, RemovalPolicy, CfnOutput, )
from constructs import Construct
import time
import uuid


class ImageBuilderPipeline(NestedStack):

    def __init__(self, scope: Construct, construct_id: str,
                 version: str,
                 bucket_name: str,
                 components_prefix: str,
                 base_image_arn: str,
                 image_pipeline_name: str,
                 instance_profile: iam.IInstanceProfile,
                 distribution_configuration: imagebuilder.CfnDistributionConfiguration,
                 removal_policy: RemovalPolicy = RemovalPolicy.RETAIN,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket_uri = "s3://" + bucket_name + "/" + components_prefix

        # [Server Hosting] How to set up a dedicated server.
        # https://steamcommunity.com/app/736220/discussions/0/2967271684632425013/

        # NOTE: when creating components, version number is supplied manually. If you update the components yaml and
        # need a new version deployed, version need to be updated manually.

        # spec to install steam components
        component_steam_uri = bucket_uri + '/install_steam_ubuntu.yml'
        component_steam = imagebuilder.CfnComponent(self,
                                                    "component_steam",
                                                    name="InstallSteam",
                                                    platform="Linux",
                                                    version=version,
                                                    uri=component_steam_uri
                                                    )
        component_steam.apply_removal_policy(removal_policy)

        # spec to install tf2
        component_tf2_uri = bucket_uri + '/install_tf2_ubuntu.yml'
        component_tf2 = imagebuilder.CfnComponent(self,
                                                      "component_tf2",
                                                      name="InstallTF2",
                                                      platform="Linux",
                                                      version=version,
                                                      uri=component_tf2_uri
                                                      )
        component_tf2.apply_removal_policy(removal_policy)

        # recipe that installs all of above components together with a ubuntu base image
        recipe = imagebuilder.CfnImageRecipe(self,
                                             f"Tf2Recipe",
                                             name=f"tf2-dedicated-server",
                                             version=version,
                                             components=[
                                                 {"componentArn": component_steam.attr_arn},
                                                 {"componentArn": component_tf2.attr_arn}
                                             ],
                                             parent_image=base_image_arn,
                                             description=f"Team Fortress 2 Dedicated Server.",
                                             block_device_mappings=[imagebuilder.CfnImageRecipe.InstanceBlockDeviceMappingProperty(
                                                 device_name='/dev/sda1',
                                                 ebs=imagebuilder.CfnImageRecipe.EbsInstanceBlockDeviceSpecificationProperty(
                                                     delete_on_termination=True,
                                                     encrypted=False,
                                                     volume_size=70,
                                                     volume_type="gp3"
                                                 ),
                                                 virtual_name="see-drive"
                                             )],
                                             working_directory='/tf2server',
                                             )
        recipe.apply_removal_policy(RemovalPolicy.DESTROY)

        # create infrastructure configuration to supply instance type
        infraconfig = imagebuilder.CfnInfrastructureConfiguration(self,
                                                                  "Tf2InfraConfig",
                                                                  name="Tf2InfraConfig",
                                                                  instance_types=[
                                                                      #   "h1.2xlarge",
                                                                      "i4g.large",
                                                                      #   "m5d.large",
                                                                      "i3.large",
                                                                      "i4i.large"],
                                                                  terminate_instance_on_failure=True,
                                                                  #   key_pair=key_pair.key_pair_name,
                                                                  instance_profile_name=instance_profile.instance_profile_name,
                                                                  )

        # build the imagebuilder pipeline
        pipeline = imagebuilder.CfnImagePipeline(self,
                                                 "Tf2Pipeline",
                                                 name=image_pipeline_name,
                                                 image_recipe_arn=recipe.attr_arn,
                                                 infrastructure_configuration_arn=infraconfig.attr_arn,
                                                 distribution_configuration_arn=distribution_configuration.attr_arn,
                                                 #  schedule=imagebuilder.CfnImagePipeline.ScheduleProperty(
                                                 #      pipeline_execution_start_condition="EXPRESSION_MATCH_AND_DEPENDENCY_UPDATES_AVAILABLE",

                                                 #      # Once a month on the first day
                                                 #      schedule_expression="cron(0 0 1 * *)"
                                                 #  ),
                                                 )
        pipeline.apply_removal_policy(removal_policy)

        pipeline.add_depends_on(infraconfig)

        # instance_profile.role.grant_assume_role(
        #     iam.ServicePrincipal("imagebuilder.amazonaws.com"))
        # lifecycle_policy = imagebuilder.CfnLifecyclePolicy(self, "MyCfnLifecyclePolicy",
        #                                                    execution_role=f"arn:aws:iam::{
        #                                                        self.account}:role/aws-service-role/imagebuilder.amazonaws.com/AWSServiceRoleForImageBuilder",
        #                                                    name=f"retire-squad44",
        #                                                    policy_details=[imagebuilder.CfnLifecyclePolicy.PolicyDetailProperty(
        #                                                        action=imagebuilder.CfnLifecyclePolicy.ActionProperty(
        #                                                            type="DELETE",

        #                                                            # the properties below are optional
        #                                                            include_resources=imagebuilder.CfnLifecyclePolicy.IncludeResourcesProperty(
        #                                                                amis=True,
        #                                                                snapshots=True
        #                                                            )
        #                                                        ),
        #                                                        filter=imagebuilder.CfnLifecyclePolicy.FilterProperty(
        #                                                            type="AGE",
        #                                                            value=1,
        #                                                            unit="DAYS",
        #                                                            # retain_at_least=1,

        #                                                        ),

        #                                                        #        # the properties below are optional
        #                                                        #        exclusion_rules=imagebuilder.CfnLifecyclePolicy.ExclusionRulesProperty(
        #                                                        #            amis=imagebuilder.CfnLifecyclePolicy.AmiExclusionRulesProperty(
        #                                                        #                is_public=False,
        #                                                        #                last_launched=imagebuilder.CfnLifecyclePolicy.LastLaunchedProperty(
        #                                                        #                    unit="unit",
        #                                                        #                    value=123
        #                                                        #                ),
        #                                                        #                regions=[
        #                                                        #                    "regions"],
        #                                                        #                shared_accounts=[
        #                                                        #                    "sharedAccounts"],
        #                                                        #                tag_map={
        #                                                        #                    "tag_map_key": "tagMap"
        #                                                        #                }
        #                                                        #            ),
        #                                                        #            tag_map={
        #                                                        #                "tag_map_key": "tagMap"
        #                                                        #            }
        #                                                        #        )
        #                                                    )],
        #                                                    resource_selection=imagebuilder.CfnLifecyclePolicy.ResourceSelectionProperty(
        #                                                        recipes=[imagebuilder.CfnLifecyclePolicy.RecipeSelectionProperty(
        #                                                            name=recipe.attr_name,
        #                                                            semantic_version=version,
        #                                                        )],
        #                                                    ),
        #                                                    resource_type="AMI_IMAGE",
        #                                                    status='ENABLED',
        #                                                    description='Delete images older than a day.',
        #                                                    )
        # lifecycle_policy.apply_removal_policy(removal_policy)
        # CfnOutput(self, "LifecyclePolicyArn", value=lifecycle_policy.attr_arn,
        #           description="The ARN of the lifecycle policy.")
        # CfnOutput(self, "LifecyclePolicyName", value=lifecycle_policy.name,
        #           description="The name of the lifecycle policy.")
        # CfnOutput(self, "LifecyclePolicyDescription", value=str(lifecycle_policy.description),
        #           description="The description of the lifecycle policy.")
        # CfnOutput(self, "LifecyclePolicyStatus", value=str(
        #     lifecycle_policy.status), description="The status of the lifecycle policy.")
