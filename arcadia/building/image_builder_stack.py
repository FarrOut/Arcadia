from aws_cdk import (
    # Duration,
    Stack, RemovalPolicy,
    # aws_sqs as sqs,
)
from constructs import Construct
from arcadia.building.images.distribution_nestedstack import Distribution
from arcadia.building.images.image_builder_pipeline_nestedstack import ImageBuilderPipeline
from arcadia.building.security.authorization_nestedstack import AuthorizationNestedStack
from arcadia.storage.build_assets_nestedstack import BuildAssetsNestedStack
from arcadia.storage.s3_nestedstack import S3NestedStack


class ImageBuilder(Stack):

    def __init__(self, scope: Construct, construct_id: str,
                 version: str,
                 removal_policy: RemovalPolicy = RemovalPolicy.DESTROY,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # s3 prefix/key for storing components
        components_prefix = "components"

        bucket = S3NestedStack(
            self, "S3NestedStack", auto_delete_objects=True, removal_policy=removal_policy).bucket

        assets_stack = BuildAssetsNestedStack(
            self, "BuildAssetsNestedStack", bucket=bucket, components_prefix=components_prefix)

        instance_profile = AuthorizationNestedStack(
            self, 'AuthorizationNestedStack', removal_policy=removal_policy).instance_profile

        distribution_configuration = Distribution(self, 'Distribution',
                                                  removal_policy=removal_policy,
                                                  version=version,
                                                  organization_arns=self.node.try_get_context(
                                                      'organization_arns'),
                                                  target_account_ids=self.node.try_get_context(
                                                      'target_account_ids'),
                                                  ).distro

        ImageBuilderPipeline(self, "ImageBuilderPipeline",
                             base_image_arn=f'arn:aws:imagebuilder:{
                                 self.region}:aws:image/ubuntu-server-20-lts-x86/2023.9.7',
                                #  amazon/ubuntu-minimal/images/hvm-ssd/ubuntu-jammy-22.04-amd64-minimal-20230921
                             image_pipeline_name='tf2-dedicated-server',
                             bucket_name=bucket.bucket_name,
                             version=version,
                             components_prefix=components_prefix,
                             instance_profile=instance_profile,
                             distribution_configuration=distribution_configuration,
                             ).add_dependency(assets_stack)
