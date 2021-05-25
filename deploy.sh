#!/bin/bash

# export AWS_DEFAULT_REGION='eu-central-1'
# export AWS_ACCESS_KEY_ID=''
# export AWS_SECRET_ACCESS_KEY=''
# export AWS_SESSION_TOKEN='''

S3_BUCKET_NAME='aws-announcement-example-bucket'
CF_STACK_NAME='announcement-app'

aws s3 mb s3://${S3_BUCKET_NAME}

aws cloudformation package \
    --template-file template.yaml \
    --s3-bucket ${S3_BUCKET_NAME} \
    --output-template-file processed_template.yaml

aws cloudformation deploy \
    --template-file processed_template.yaml \
    --stack-name ${CF_STACK_NAME} \
    --capabilities CAPABILITY_IAM

api_endpoint=$(aws cloudformation describe-stacks --stack-name "${CF_STACK_NAME}" \
    --query "Stacks[].Outputs[? OutputKey == 'ApiUrl'].OutputValue" \
    --output text)

echo "The API is available at ${api_endpoint}"