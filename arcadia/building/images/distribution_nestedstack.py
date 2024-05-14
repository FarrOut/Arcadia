from typing import Sequence
from aws_cdk import (
    # Duration,
    aws_s3 as s3,
    aws_imagebuilder as imagebuilder,
    aws_iam as iam,
    NestedStack,
    RemovalPolicy,
    CfnOutput,
)
from constructs import Construct


class Distribution(NestedStack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        version: str,
        target_account_ids: Sequence[str],
        organization_arns: Sequence[str],
        removal_policy: RemovalPolicy = RemovalPolicy.RETAIN,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.distro = imagebuilder.CfnDistributionConfiguration(
            self,
            "MyCfnDistributionConfiguration",
            distributions=[
                imagebuilder.CfnDistributionConfiguration.DistributionProperty(
                    region=self.region,
                    ami_distribution_configuration=imagebuilder.CfnDistributionConfiguration.AmiDistributionConfigurationProperty(
                        ami_tags={
                            "Application": "rising-storm-2-vietnam-dedicated-server",
                            "Version": version,
                            "Owner": self.account,
                        },
                        description=f"Avail AMI to {self.region}",
                        launch_permission_configuration=imagebuilder.CfnDistributionConfiguration.LaunchPermissionConfigurationProperty(
                            organization_arns=organization_arns,
                        ),
                        name="rs2-vietnam-dedicated-server {{ imagebuilder:buildDate }}",
                        target_account_ids=target_account_ids,
                    ),
                )
            ],
            name="rs2-vietnam-dedicated-server",
            description="Rising Storm 2 Vietnam Dedicated Server.",
        )
        self.distro.apply_removal_policy(removal_policy)

        CfnOutput(self, "DistributionArn", value=self.distro.attr_arn)
        CfnOutput(self, "DistributionName", value=self.distro.name)
        CfnOutput(self, "DistributionVersion", value=version)
        CfnOutput(self, "DistributionOwner", value=self.account)
        # CfnOutput(
        #     self, "DistributionTargetAccountIds", value=",".join(target_account_ids)
        # )
        # CfnOutput(
        #     self, "DistributionOrganizationArns", value=",".join(organization_arns)
        # )
        CfnOutput(self, "DistributionDescription", value=self.distro.description)
