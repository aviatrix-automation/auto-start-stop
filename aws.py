import boto3

# Get list of regions
def get_regions():
    ec2 = boto3.client("ec2", region_name="us-east-1")
    response = ec2.describe_regions()
    regions = response["Regions"]
    list_of_regions = []
    for region in regions:
        list_of_regions.append(region["RegionName"])
    return list_of_regions


# Get list of running/stopped instances in a region
def get_instances(region, state):
    ec2 = boto3.client("ec2", region_name=region)
    response = ec2.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": [state]}]
    )
    instances = response["Reservations"]
    list_of_instances = []
    for instance in instances:
        list_of_instances.append(instance["Instances"][0]["InstanceId"])
    return list_of_instances


# Stop instances in all regions
def stop_instances():
    list_of_regions = get_regions()
    for region in list_of_regions:
        ec2 = boto3.client("ec2", region_name=region)
        instances = get_instances(region, "running")
        if len(instances) == 0:
            print("No instances to stop in", region)
        else:
            ec2.stop_instances(InstanceIds=instances)
            print("Stopping instsances in", region, instances)


# Start instances in all regions
def start_instances():
    list_of_regions = get_regions()
    for region in list_of_regions:
        ec2 = boto3.client("ec2", region_name=region)
        instances = get_instances(region, "stopped")
        if len(instances) == 0:
            print("No instances to start in", region)
        else:
            ec2.start_instances(InstanceIds=instances)
            print("Starting instances in", region, instances)


def lambda_handler(event, context):
    #    stop_instances()
    start_instances()
