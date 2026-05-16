import aws_cdk as core
import aws_cdk.assertions as assertions
from stablediffusion_lambda.stablediffusion_lambda_stack import StablediffusionLambdaStack


def test_s3_bucket_created():
    app = core.App()
    stack = StablediffusionLambdaStack(app, "stablediffusion-lambda")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::S3::Bucket", {
        "LifecycleConfiguration": {
            "Rules": [
                {
                    "ExpirationInDays": 1,
                }
            ]
        }
    })


def test_s3_bucket_block_public_access():
    app = core.App()
    stack = StablediffusionLambdaStack(app, "stablediffusion-lambda")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::S3::BucketPolicy", {})


def test_lambda_function_created():
    app = core.App()
    stack = StablediffusionLambdaStack(app, "stablediffusion-lambda")
    template = assertions.Template.from_stack(stack)

    # DockerImageFunction uses Architectures (array) in CloudFormation
    template.has_resource_properties("AWS::Lambda::Function", {
        "Architectures": ["arm64"],
        "Timeout": 900,
        "MemorySize": 10000,
        "PackageType": "Image",
    })


def test_lambda_role_created():
    app = core.App()
    stack = StablediffusionLambdaStack(app, "stablediffusion-lambda")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::IAM::Role", {
        "AssumeRolePolicyDocument": {
            "Statement": [
                {
                    "Principal": {
                        "Service": "lambda.amazonaws.com",
                    }
                }
            ]
        }
    })


def test_lambda_function_url_created():
    app = core.App()
    stack = StablediffusionLambdaStack(app, "stablediffusion-lambda")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::Lambda::Url", {
        "AuthType": "NONE",
    })


def test_lambda_function_url_cors():
    app = core.App()
    stack = StablediffusionLambdaStack(app, "stablediffusion-lambda")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::Lambda::Url", {
        "Cors": {
            "AllowOrigins": ["*"],
        }
    })


def test_s3_bucket_grants_to_lambda():
    app = core.App()
    stack = StablediffusionLambdaStack(app, "stablediffusion-lambda")
    template = assertions.Template.from_stack(stack)

    # grant_read_write creates an IAM policy on the Lambda role
    # Stack has 3 policies: S3 bucket policy, Lambda role default policy, LogRetention policy
    template.resource_count_is("AWS::IAM::Policy", 2)


def test_cfn_output_stable_diffusion_url():
    app = core.App()
    stack = StablediffusionLambdaStack(app, "stablediffusion-lambda")
    template = assertions.Template.from_stack(stack)

    template.has_output("StableDiffusionUrl", {})
