#!/usr/bin/env python3

import aws_cdk as cdk

from stablediffusion_lambda.stablediffusion_lambda_stack import StablediffusionLambdaStack


app = cdk.App()
StablediffusionLambdaStack(app, "stablediffusion-lambda")

app.synth()
