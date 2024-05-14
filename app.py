#!/usr/bin/env python3
import os

from aws_cdk import (
    Duration, App, Environment,
    aws_s3 as s3, aws_iam as iam, aws_ec2 as ec2,
    NestedStack, RemovalPolicy, CfnOutput, )

from arcadia.server_stack import Server

from arcadia.building.image_builder_stack import ImageBuilder



default_env = Environment(account=os.getenv(
    'CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION'))
africa_env = Environment(account=os.getenv(
    'CDK_DEFAULT_ACCOUNT'), region='af-south-1')

app = App()

version = "0.0.1"

peers = app.node.try_get_context("peers")
key_name = app.node.try_get_context("key_name")

image_builder = ImageBuilder(app, "ImageBuilder",
                                    env=africa_env,
                                    version=version,
                                    removal_policy=RemovalPolicy.DESTROY,
                                    )

# Server(app, "Server",
#               env=africa_env,
#               whitelisted_peer=ec2.Peer.prefix_list(peers),
#               key_name=key_name,
#               removal_policy=RemovalPolicy.DESTROY,
#               )

# WatchdogStack(app, "WatchdogSquad44",
#               env=africa_env,
#               removal_policy=RemovalPolicy.DESTROY,
#               )

app.synth()
