from aws_cdk import (
    # Duration,
    aws_s3 as s3, aws_imagebuilder as imagebuilder,
    aws_iam as iam,
    NestedStack, RemovalPolicy, CfnOutput, )
from constructs import Construct
import time
import uuid


class ImageBuilderWindowsPipeline(NestedStack):

    def __init__(self, scope: Construct, construct_id: str,
                 version: str,
                 bucket_name: str,
                 components_prefix: str,
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

        # spec to install OS updates
        component_os_uri = bucket_uri + '/prep_os_windows.yml'
        component_os = imagebuilder.CfnComponent(self,
                                                    "component_prep_windows",
                                                    name="PrepWindows",
                                                    platform="Windows",
                                                    version=version,
                                                    uri=component_os_uri
                                                    )
        component_os.apply_removal_policy(removal_policy)

        # spec to install steam components
        component_steam_uri = bucket_uri + '/install_steam_windows.yml'
        component_steam = imagebuilder.CfnComponent(self,
                                                    "component_steam",
                                                    name="InstallSteam",
                                                    platform="Windows",
                                                    version=version,
                                                    uri=component_steam_uri
                                                    )
        component_steam.apply_removal_policy(removal_policy)

        # spec to install tf2
        component_game_uri = bucket_uri + '/install_rs2vietnam_windows.yml'
        component_game = imagebuilder.CfnComponent(self,
                                                      "component_game",
                                                      name="InstallGame",
                                                      platform="Windows",
                                                      version=version,
                                                      uri=component_game_uri
                                                      )
        component_game.apply_removal_policy(removal_policy)

        base_image_arn=f'arn:aws:imagebuilder:{
                                 self.region}:aws:image/ubuntu-server-20-lts-x86/2023.9.7',
        base_image_arn='ami-0092a751c04951b01' # TODO hard-code override. af-south-1 region

        # recipe that installs all of above components together with a ubuntu base image
        recipe = imagebuilder.CfnImageRecipe(self,
                                             f"RS2VietnamRecipe",
                                             name=f"rising-storm-2-vietnam-dedicated-server",
                                             version=version,
                                             components=[
                                                 {"componentArn": component_os.attr_arn},
                                                 {"componentArn": component_steam.attr_arn},
                                                 {"componentArn": component_game.attr_arn}
                                             ],
                                             parent_image=base_image_arn,
                                             description=f"Rising Storm 2 Vietnam Dedicated Server.",
                                             block_device_mappings=[imagebuilder.CfnImageRecipe.InstanceBlockDeviceMappingProperty(
                                                 device_name='xvdb',
                                                 ebs=imagebuilder.CfnImageRecipe.EbsInstanceBlockDeviceSpecificationProperty(
                                                     delete_on_termination=True,
                                                     encrypted=False,
                                                     volume_size=50,
                                                     volume_type="gp3"
                                                 ),
                                                 virtual_name="see-drive"
                                             )],
                                            #  working_directory='c:\\gameserver',
                                             )
        recipe.apply_removal_policy(RemovalPolicy.DESTROY)

        # create infrastructure configuration to supply instance type
        infraconfig = imagebuilder.CfnInfrastructureConfiguration(self,
                                                                  "InfraConfig",
                                                                  name="ArcadiaInfraConfig",
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
                                                 "ArcadiaPipeline",
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
