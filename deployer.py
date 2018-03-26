import boto3
import json
import time
import argparse

# TODO, some of those infomration might go with env
TEMPLATE = 'https://s3.amazonaws.com/quickstart-reference/splunk/enterprise/latest/templates/splunk-enterprise-master.template'
PASSWORD = 'K8scicd!'
LICENSE_BUCKET = 'pr45-k8s-ci'
LICENSE_PATH = 'splunk-licenses/Splunk_Enterprise_NFR_Q1FY19.lic'
KEYPAIR_NAME = 'pr45-k8s-ci'

def create_stack(name):
    client = boto3.client('cloudformation')
    response = client.create_stack(
        StackName=name,
        TemplateURL=TEMPLATE,
        Parameters=[
            {
                'ParameterKey': 'AvailabilityZones',
                'ParameterValue': 'us-east-1a,us-east-1b'
            },
            {
                'ParameterKey': 'HECClientLocation',
                'ParameterValue': '0.0.0.0/0'
            },
            {
                'ParameterKey': 'IndexerInstanceType',
                'ParameterValue': 'c4.large'
            },
            {
                'ParameterKey': 'KeyName',
                'ParameterValue': KEYPAIR_NAME
            },
            {
                'ParameterKey': 'NumberOfAZs',
                'ParameterValue': '2'
            },
            {
                'ParameterKey': 'PublicSubnet1CIDR',
                'ParameterValue': '10.0.1.0/24'
            },
            {
                'ParameterKey': 'PublicSubnet2CIDR',
                'ParameterValue': '10.0.2.0/24'
            },
            {
                'ParameterKey': 'PublicSubnet3CIDR',
                'ParameterValue': '10.0.3.0/24'
            },
            {
                'ParameterKey': 'QSS3BucketName',
                'ParameterValue': 'quickstart-reference'
            },
            {
                'ParameterKey': 'QSS3KeyPrefix',
                'ParameterValue': 'splunk/enterprise/latest/'
            },
            {
                'ParameterKey': 'SearchHeadInstanceType',
                'ParameterValue': 'c4.large'
            },
            {
                'ParameterKey': 'SHCEnabled',
                'ParameterValue': 'no'
            },
            {
                'ParameterKey': 'SplunkAdminPassword',
                'ParameterValue': PASSWORD
            },
            {
                'ParameterKey': 'SplunkClusterSecret',
                'ParameterValue': PASSWORD
            },
            {
                'ParameterKey': 'SplunkIndexerDiscoverySecret',
                'ParameterValue': PASSWORD
            },
            {
                'ParameterKey': 'SplunkIndexerCount',
                'ParameterValue': '3'
            },
            {
                'ParameterKey': 'SplunkIndexerDiskSize',
                'ParameterValue': '100'
            },
            {
                'ParameterKey': 'SplunkLicenseBucket',
                'ParameterValue': LICENSE_BUCKET
            },
            {
                'ParameterKey': 'SplunkLicensePath',
                'ParameterValue': LICENSE_PATH
            },
            {
                'ParameterKey': 'SplunkReplicationFactor',
                'ParameterValue': '3'
            },
            {
                'ParameterKey': 'SSHClientLocation',
                'ParameterValue': '0.0.0.0/0'
            },
            {
                'ParameterKey': 'VPCCIDR',
                'ParameterValue': '10.0.0.0/16'
            },
            {
                'ParameterKey': 'WebClientLocation',
                'ParameterValue': '0.0.0.0/0'
            },
        ],
        Capabilities=[
            'CAPABILITY_IAM'
        ]
    )

    while True:
        response = client.describe_stacks(
            StackName=name
        )

        status = response["Stacks"][0]["StackStatus"]
        if status == "CREATE_IN_PROGRESS":
            time.sleep(3)
            continue
        outputs = response["Stacks"][0]["Outputs"]
        return outputs


def delete_stack(name):
    client = boto3.client('cloudformation')
    response = client.delete_stack(
        StackName=name,
    )
    while True:
        try:
            response = client.describe_stacks(
                StackName=name
            )

            status = response["Stacks"][0]["StackStatus"]
            if status != "DELETE_IN_PROGRESS":
                break
            time.sleep(3)
        except:
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Splunk AWS deployment')
    parser.add_argument('op', choices=['create', 'delete'])
    parser.add_argument('--name')

    args = parser.parse_args()
    if args.op == "create":
        outputs = json.dumps(create_stack(args.name))
        print(outputs)
        with open("/data/stack_output.json","w") as f:
            f.write(outputs)
    elif args.op == "delete":
        delete_stack(args.name)