import aws_cdk as core
import aws_cdk.assertions as assertions

from arcadia.building.image_builder_stack import Squad44DedicatedServerStack

# example tests. To run these tests, uncomment this file along with the example
# resource in squad44_dedicated_server/squad44_dedicated_server_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = Squad44DedicatedServerStack(app, "squad44-dedicated-server")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
