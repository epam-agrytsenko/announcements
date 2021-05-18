#!/bin/bash

# export AWS_DEFAULT_REGION='eu-central-1'
# export AWS_ACCESS_KEY_ID=''
# export AWS_SECRET_ACCESS_KEY=''
# export AWS_SESSION_TOKEN='''

S3_BUCKET_NAME='aws-announcement-example-bucket'
CF_STACK_NAME='announcement-app'
LOG_GROUP_PATTERN='announcement-app'


aws cloudformation delete-stack \
    --stack-name "${CF_STACK_NAME}"

aws cloudformation wait stack-delete-complete \
    --stack-name "${CF_STACK_NAME}"

log_groups_to_delete=$(aws logs describe-log-groups \
    --query "logGroups[? contains(logGroupName, '${LOG_GROUP_PATTERN}')].logGroupName" \
    --output text)
for log_group in ${log_groups_to_delete}; do
    aws logs delete-log-group --log-group-name "${log_group}" > /dev/null
    echo "deleted log group ${log_group}"
done

set +e
aws s3 rb s3://${S3_BUCKET_NAME} --force
echo "Application cleanup is finished!"