import boto3

# Only instances with this tag will be autostarted
tag_include_autostart = {"Key": "Auto-Start", "Value": "True"}


# All instances will be autostopped unless it has this tag
tag_exclude_autostop = {"Key": "Auto-Stop", "Value": "False"}


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


# Filters a list of instances based on a tag and an action (include or exclude)
# - include will return a list of instances that have this tag
# - exclude will return a list of instances that do not have this tag
def filter_list(instance_list, region, tag, action):
    filtered_list = []
    ec2 = boto3.client("ec2", region_name=region)
    if action == "include":
        for instance in instance_list:
            response = ec2.describe_instances(
                Filters=[{"Name": "instance-id", "Values": [instance]}]
            )
            if "Tags" in response["Reservations"][0]["Instances"][0]:
                instance_tags = response["Reservations"][0]["Instances"][0]["Tags"]
                if tag in instance_tags:
                    filtered_list.append(instance)
    if action == "exclude":
        for instance in instance_list:
            response = ec2.describe_instances(
                Filters=[{"Name": "instance-id", "Values": [instance]}]
            )
            if "Tags" in response["Reservations"][0]["Instances"][0]:
                instance_tags = response["Reservations"][0]["Instances"][0]["Tags"]
                if tag not in instance_tags:
                    filtered_list.append(instance)
            else:
                # Instance doesn't have tags so add it to the filtered list
                filtered_list.append(instance)
    return filtered_list


# Start instances in all regions that have the the tag_include_autostart tag
def start_instances():
    list_of_regions = get_regions()
    for region in list_of_regions:
        ec2 = boto3.client("ec2", region_name=region)
        instances = get_instances(region, "stopped")
        filtered_list = filter_list(instances, region, tag_include_autostart, "include")
        if len(filtered_list) == 0:
            print("No instances to start in", region)
        else:
            ec2.start_instances(InstanceIds=filtered_list)
            print("Starting instances in", region, filtered_list)


# Stop instances in all regions that don't have the tag_exclude_autostop tag
def stop_instances():
    list_of_regions = get_regions()
    for region in list_of_regions:
        ec2 = boto3.client("ec2", region_name=region)
        instances = get_instances(region, "running")
        filtered_list = filter_list(instances, region, tag_exclude_autostop, "exclude")
        if len(filtered_list) == 0:
            print("No instances to stop in", region)
        else:
            ec2.stop_instances(InstanceIds=filtered_list)
            print("Stopping instances in", region, filtered_list)


def lambda_handler(event, context):
    stop_instances()


# stop_instances()
start_instances()
