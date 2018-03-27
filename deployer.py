import boto3
import json
import time
import argparse
import os

# TODO, some of those infomration might go with env
TEMPLATE = 'https://s3.amazonaws.com/quickstart-reference/splunk/enterprise/latest/templates/splunk-enterprise-master.template'
PASSWORD = 'K8scicd!'
LICENSE_BUCKET = 'pr45-k8s-ci'
LICENSE_PATH = 'splunk-licenses/Splunk_Enterprise_NFR_Q1FY19.lic'

STACK_OUTPUT_FILE = "/data/stack_output.json"

# keypiar and AZ are region sepcific, we may want to add these into env
KEYPAIR_NAME = 'pr45-k8s-ci'
AZ_VALUES = 'us-east-1a,us-east-1b'

def _get_vpc_output(name):
    client = boto3.client('cloudformation')
    response = client.describe_stack_resource(
        StackName=name,
        LogicalResourceId='VPCStack'
    )

    vpc_stack_id = response["StackResourceDetail"]["PhysicalResourceId"]
    response = client.describe_stacks(
        StackName=vpc_stack_id
    )
    vpc_output = response["Stacks"][0]["Outputs"]
    return vpc_output

def create_stack(name):
    client = boto3.client('cloudformation')
    response = client.create_stack(
        StackName=name,
        TemplateURL=TEMPLATE,
        Parameters=[
            {
                'ParameterKey': 'AvailabilityZones',
                'ParameterValue': AZ_VALUES
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
        ],
        OnFailure='DO_NOTHING'
    )

    result = dict()

    while True:
        response = client.describe_stacks(
            StackName=name
        )

        status = response["Stacks"][0]["StackStatus"]
        if status == "CREATE_IN_PROGRESS":
            time.sleep(3)
            continue
        # TODO check the nested stack of VPC stack
        outputs = response["Stacks"][0]["Outputs"]
        result["SplunkStack"] = outputs
        break

    vpc_output = _get_vpc_output(name)
    result["VPCStack"] = vpc_output
    return result


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
    parser.add_argument('--output')

    args = parser.parse_args()
    if args.output is not None:
        STACK_OUTPUT_FILE = args.output

    if args.op == "create":
        outputs_obj = create_stack(args.name)
        outputs_str = json.dumps(outputs_obj)
        print(outputs_str)
        with open(STACK_OUTPUT_FILE, "w") as f:
            f.write(outputs_str)
    elif args.op == "delete":
        delete_stack(args.name)
