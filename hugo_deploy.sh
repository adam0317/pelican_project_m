export AWS_BUCKET_NAME="s3://$1/"
export STAGING_PATH=/Users/adam.windsor/sitegrinder/sites/staging/wasabi/$1


aws s3 mv --profile wasabi --recursive $STAGING_PATH $AWS_BUCKET_NAME  --endpoint-url=https://s3.us-west-1.wasabisys.com

