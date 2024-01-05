from aws_cdk import (
    # Duration,
    aws_s3 as s3, aws_s3_deployment as s3_deployment,
    NestedStack, RemovalPolicy, CfnOutput, )
from constructs import Construct


class BuildAssetsNestedStack(NestedStack):

    def __init__(self, scope: Construct, construct_id: str,
                 bucket: s3.IBucket,
                 components_prefix: str = "components",
                 removal_policy: RemovalPolicy = RemovalPolicy.RETAIN,

                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # set component folder as source for deployment
        source_asset = s3_deployment.Source.asset('./components')

        # deploy everything under folder to s3 bucket
        s3_deployment.BucketDeployment(self,
                                       "stacks_components_deployment",
                                       destination_bucket=bucket,
                                       sources=[source_asset],
                                       destination_key_prefix=components_prefix,
                                       )

        CfnOutput(self, 'BucketArn',
                  description='The ARN of the bucket.',
                  value=bucket.bucket_arn,
                  )
        CfnOutput(self, 'BucketDomainName',
                  description='The IPv4 DNS name of the specified bucket.',
                  value=bucket.bucket_domain_name,
                  )
        CfnOutput(self, 'BucketName',
                  description='The name of the bucket.',
                  value=bucket.bucket_name,
                  )
        CfnOutput(self, 'BucketWebsiteUrl',
                  description='The URL of the static website.',
                  value=str(bucket.bucket_website_url),
                  )
        CfnOutput(self, 'BucketUri',
                  description='The Uri of the bucket.',
                  value=str('s3://{}'.format(bucket.bucket_name)),
                  )
