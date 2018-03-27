# Create Stack
```
docker run --rm -it \
  -e "AWS_ACCESS_KEY_ID=<id>" \
  -e "AWS_SECRET_ACCESS_KEY=<key>" \
  -e "AWS_DEFAULT_REGION=<region>" \
  -v /data:/data \
  splunk-aws-deployer create --name <stack_name>
```
# Delete Stack
```
docker run --rm -it \
  -e "AWS_ACCESS_KEY_ID=<id>" \
  -e "AWS_SECRET_ACCESS_KEY=<key>" \
  -e "AWS_DEFAULT_REGION=<region>" \
  splunk-aws-deployer delete --name <stack_name>
```