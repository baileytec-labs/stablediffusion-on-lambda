from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_lambda as aws_lambda,
    aws_logs as logs,
    CfnOutput,
    aws_s3 as s3

)
import aws_cdk as cdk




class StablediffusionLambdaStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create the S3 bucket
        sd_storage_bucket = s3.Bucket(self, "sd-storage-bucket",
            bucket_name="sd-storage-bucket",
            removal_policy=cdk.RemovalPolicy.DESTROY,  # Delete bucket contents when the stack is deleted
            auto_delete_objects=True,  # Automatically delete objects when the bucket is removed
            lifecycle_rules=[
                s3.LifecycleRule(
                    expiration=Duration.days(1),  # Delete objects after 24 hours
                )
            ],
            public_read_access=False,  # Ensure the bucket is not public
        )

        #--------------------------------------Stable Diffusion Lambda Function---------------------------------------------
        stable_diffusion_lambda_function_name="stable_diffusion_lambda_function"

        stable_diffusion_lambda_role=iam.Role(
            self,
            id="stable_diffusion_lambda_role",
            assumed_by = iam.ServicePrincipal("lambda.amazonaws.com")
        )

        stable_diffusion_lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaBasicExecutionRole"
            )
        )

        stable_diffusion_lambda_function=aws_lambda.DockerImageFunction(self,stable_diffusion_lambda_function_name,
        architecture=aws_lambda.Architecture.ARM_64,
        timeout=Duration.seconds(900),
        log_retention=logs.RetentionDays.ONE_WEEK,
        environment={

        "STAGE":"",
        "BUCKET_NAME":sd_storage_bucket.bucket_name,
        },
        memory_size=4000,
        retry_attempts=0,
        role=stable_diffusion_lambda_role,
        code=aws_lambda.DockerImageCode.from_image_asset("./stablediffusion_cpp_docker"),
        )

        stable_diffusion_lambda_function_url=stable_diffusion_lambda_function.add_function_url(
            auth_type=aws_lambda.FunctionUrlAuthType.NONE,
            cors=aws_lambda.FunctionUrlCorsOptions(
         #Allow this to be called from websites on https://example.com.
         #Can also be ['*'] to allow all domain.
        allowed_origins=["*"]
        )
        #we need to allow all interactions with this url
        )

        

        # Grant the Lambda function full permissions to the S3 bucket
        sd_storage_bucket.grant_read_write(stable_diffusion_lambda_function)



        CfnOutput(self, "StableDiffusionUrl",
        value=stable_diffusion_lambda_function_url.url + "docs"
        )