import boto3
import json


def run_security_audit(profile, region, dry_run=False):
    session = boto3.Session(profile_name=profile, region_name=region)
    iam = session.client('iam')

    report = {}

    # Example check: Users without MFA
    users = iam.list_users()['Users']
    no_mfa_users = []
    for user in users:
        mfa = iam.list_mfa_devices(UserName=user['UserName'])
        if len(mfa['MFADevices']) == 0:
            no_mfa_users.append(user['UserName'])

    report['users_without_mfa'] = no_mfa_users

    if not dry_run:
        with open('reports/security_report.json', 'w') as f:
            json.dump(report, f, indent=2)

    return report
