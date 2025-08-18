import boto3
import csv
from datetime import datetime, timedelta

# Config
REGION = "ap-south-1"   # Change to your AWS region
OUTPUT_FILE = "ebs_usage_report.csv"
DAYS = 30

# Initialize clients
ec2 = boto3.client("ec2", region_name=REGION)
cloudwatch = boto3.client("cloudwatch", region_name=REGION)

end_time = datetime.utcnow()
start_time = end_time - timedelta(days=DAYS)

def get_metric_sum(volume_id, metric_name):
    """Fetch CloudWatch metric sum for the volume"""
    response = cloudwatch.get_metric_statistics(
        Namespace="AWS/EBS",
        MetricName=metric_name,
        Dimensions=[{"Name": "VolumeId", "Value": volume_id}],
        StartTime=start_time,
        EndTime=end_time,
        Period=2592000,  # 30 days in seconds
        Statistics=["Sum"]
    )
    datapoints = response.get("Datapoints", [])
    if datapoints:
        return datapoints[0]["Sum"]
    return 0

def main():
    volumes = ec2.describe_volumes()["Volumes"]

    results = []
    used_count = 0
    unused_count = 0

    for vol in volumes:
        vol_id = vol["VolumeId"]
        state = vol["State"]
        size = vol["Size"]
        az = vol["AvailabilityZone"]

        # Fetch read + write ops
        read_ops = get_metric_sum(vol_id, "VolumeReadOps")
        write_ops = get_metric_sum(vol_id, "VolumeWriteOps")

        if (read_ops + write_ops) == 0:
            usage_status = "Not Used"
            unused_count += 1
        else:
            usage_status = "Used"
            used_count += 1

        results.append({
            "VolumeId": vol_id,
            "State": state,
            "Size": size,
            "AZ": az,
            "ReadOps": read_ops,
            "WriteOps": write_ops,
            "UsageStatus": usage_status
        })

    # Write to CSV
    with open(OUTPUT_FILE, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "VolumeId", "State", "Size", "AZ", "ReadOps", "WriteOps", "UsageStatus"
        ])
        writer.writeheader()
        writer.writerows(results)

    print(f"Report saved to {OUTPUT_FILE}")
    print(f"Summary: {used_count} volumes USED, {unused_count} volumes NOT USED in last {DAYS} days.")

if __name__ == "__main__":
    main()
