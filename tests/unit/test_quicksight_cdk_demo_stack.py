import aws_cdk as core
import aws_cdk.assertions as assertions

from quicksight_cdk_demo.quicksight_cdk_demo_stack import QuicksightCdkDemoStack

# example tests. To run these tests, uncomment this file along with the example
# resource in quicksight_cdk_demo/quicksight_cdk_demo_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = QuicksightCdkDemoStack(app, "quicksight-cdk-demo")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
