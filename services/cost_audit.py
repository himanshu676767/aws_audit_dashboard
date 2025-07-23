# import boto3
# import json
#
# def run_cost_audit(profile, region, dry_run=False):
#     session = boto3.Session(profile_name=profile, region_name=region)
#     ec2 = session.client('ec2')
#
#     report = {}
#
#     # Sample: Unused EBS
#     volumes = ec2.describe_volumes(Filters=[{'Name': 'status', 'Values': ['available']}])
#     report['unused_ebs_volumes'] = len(volumes['Volumes'])
#
#     # Other checks: Elastic IPs, Snapshots, Stopped EC2, Security groups
#
#     if not dry_run:
#         with open('reports/cost_report.json', 'w') as f:
#             json.dump(report, f, indent=2)
#
#     return report



import boto3
import json
from datetime import datetime, timedelta

def run_cost_audit(profile, region, dry_run=False):
    session = boto3.Session(profile_name=profile, region_name=region)
    client = session.client('ce')  # Cost Explorer

    # Dates
    end = datetime.utcnow().date()
    start = (end - timedelta(days=30)).isoformat()
    end = end.isoformat()

    try:
        response = client.get_cost_and_usage(
            TimePeriod={'Start': start, 'End': end},
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            GroupBy=[
                {'Type': 'DIMENSION', 'Key': 'REGION'}
            ]
        )
    except Exception as e:
        return {"error": str(e)}

    cost_summary = {}
    for group in response['ResultsByTime'][0]['Groups']:
        region_key = group['Keys'][0]
        amount = group['Metrics']['UnblendedCost']['Amount']
        cost_summary[region_key] = round(float(amount), 2)

    result = {
        "profile": profile,
        "start_date": start,
        "end_date": end,
        "regional_costs": cost_summary
    }

    if not dry_run:
        with open("reports/cost_report.json", "w") as f:
            json.dump(result, f, indent=2)

    return result
