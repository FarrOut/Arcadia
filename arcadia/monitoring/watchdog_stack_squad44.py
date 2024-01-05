from aws_cdk import (
    # Duration,
    Stack, RemovalPolicy, CfnOutput,
    aws_resourcegroups as resourcegroups
)
from constructs import Construct
from arcadia.monitoring.anomaly_monitor_nestedstack import AnomalyMonitor
from arcadia.monitoring.resource_explorer_nestedstack import ResourceExplorer
from arcadia.storage.build_assets_nestedstack import BuildAssetsNestedStack
from arcadia.storage.s3_nestedstack import S3NestedStack


class WatchdogStack(Stack):

    def __init__(self, scope: Construct, construct_id: str,
                 removal_policy: RemovalPolicy = RemovalPolicy.RETAIN,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ResourceExplorer(self, "ResourceExplorer",
                         removal_policy=removal_policy)
        # AnomalyMonitor(self, "AnomalyMonitor",)
