from aws_cdk import (
    # Duration,
    aws_s3 as s3, aws_iam as iam, aws_resourcegroups as resourcegroups, aws_ce as ce,
    NestedStack, RemovalPolicy, CfnOutput, )
from constructs import Construct


class AnomalyMonitor(NestedStack):

    def __init__(self, scope: Construct, construct_id: str,
                 removal_policy: RemovalPolicy = RemovalPolicy.RETAIN,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        anomaly_monitor = ce.CfnAnomalyMonitor(self, "AnomalyMonitor",
                                               monitor_name="Squad44Anomalies",
                                               monitor_type="CUSTOM",

                                               monitor_specification="{\"Tags\": {\"Key\": \"PropertyOf\", \"Values\": [\"squad44-dedicated-server\"]}}",
                                               )
        anomaly_monitor.apply_removal_policy(removal_policy)

        CfnOutput(self, "AnomalyMonitorArn", value=anomaly_monitor.attr_monitor_arn,
                  description="The Amazon Resource Name (ARN) value for the monitor.", export_name="AnomalyMonitorArn")
        CfnOutput(self, "AnomalyMonitorName", value=anomaly_monitor.monitor_name,
                  description="The name of the monitor.",)
        CfnOutput(self, "CreationDate", value=anomaly_monitor.attr_creation_date,
                  description="The date when the monitor was created.",)
