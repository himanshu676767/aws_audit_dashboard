# import boto3
# import json
#
#
# def run_security_audit(profile, region, dry_run=False):
#     session = boto3.Session(profile_name=profile, region_name=region)
#     iam = session.client('iam')
#
#     report = {}
#
#     # Example check: Users without MFA
#     users = iam.list_users()['Users']
#     no_mfa_users = []
#     for user in users:
#         mfa = iam.list_mfa_devices(UserName=user['UserName'])
#         if len(mfa['MFADevices']) == 0:
#             no_mfa_users.append(user['UserName'])
#
#     report['users_without_mfa'] = no_mfa_users
#
#     if not dry_run:
#         with open('reports/security_report.json', 'w') as f:
#             json.dump(report, f, indent=2)
#
#     return report




import boto3
import json

#
# def run_security_audit(profile, region, dry_run=False):
#     session = boto3.Session(profile_name=profile, region_name=region)
#     iam = session.client('iam')
#
#     report = {}
#
#     users = iam.list_users()['Users']
#     no_mfa_users = []
#     mfa_users = []
#
#     for user in users:
#         user_name = user['UserName']
#         mfa = iam.list_mfa_devices(UserName=user_name)
#
#         if len(mfa['MFADevices']) == 0:
#             no_mfa_users.append(user_name)
#         else:
#             mfa_users.append({
#                 "user": user_name,
#                 "mfa_devices": [
#                     {
#                         "serial_number": device['SerialNumber'],
#                         "enable_date": str(device.get('EnableDate', 'N/A'))
#                     }
#                     for device in mfa['MFADevices']
#                 ]
#             })
#
#     report['users_without_mfa'] = no_mfa_users
#     report['users_with_mfa'] = mfa_users
#
#     if not dry_run:
#         with open('reports/security_report.json', 'w') as f:
#             json.dump(report, f, indent=2)
#
#     return report
#




import boto3
import json
from datetime import datetime, timezone


def run_security_audit(profile, region, dry_run=False):
    session = boto3.Session(profile_name=profile, region_name=region)
    iam = session.client('iam')
    s3 = session.client('s3')

    report = {}

    ### 1. IAM Audit ###
    users = iam.list_users()['Users']
    users_without_mfa = []
    users_with_mfa = []
    old_access_keys = []
    wildcard_policies = []

    for user in users:
        user_name = user['UserName']

        # MFA check
        mfa_devices = iam.list_mfa_devices(UserName=user_name)
        if not mfa_devices['MFADevices']:
            users_without_mfa.append(user_name)
        else:
            users_with_mfa.append(user_name)

        # Access key check (older than 90 days)
        keys = iam.list_access_keys(UserName=user_name)['AccessKeyMetadata']
        for key in keys:
            created = key['CreateDate']
            age_days = (datetime.now(timezone.utc) - created).days
            if age_days > 90:
                old_access_keys.append({
                    "user": user_name,
                    "access_key_id": key['AccessKeyId'],
                    "age_days": age_days
                })

        # Inline or wildcard policy check
        attached_policies = iam.list_attached_user_policies(UserName=user_name)['AttachedPolicies']
        for policy in attached_policies:
            policy_version = iam.get_policy(PolicyArn=policy['PolicyArn'])['Policy']['DefaultVersionId']
            policy_doc = iam.get_policy_version(
                PolicyArn=policy['PolicyArn'],
                VersionId=policy_version
            )['PolicyVersion']['Document']

            statements = policy_doc.get('Statement', [])
            if not isinstance(statements, list):
                statements = [statements]
            for stmt in statements:
                if stmt.get('Action') == "*" or stmt.get('Resource') == "*":
                    wildcard_policies.append({
                        "user": user_name,
                        "policy_name": policy['PolicyName'],
                        "arn": policy['PolicyArn']
                    })

    report['iam'] = {
        "users_without_mfa": users_without_mfa,
        "users_with_mfa": users_with_mfa,
        "old_access_keys": old_access_keys,
        "wildcard_policies": wildcard_policies
    }

    ### 2. S3 Audit ###
    public_buckets = []
    unencrypted_buckets = []

    buckets = s3.list_buckets()['Buckets']
    for bucket in buckets:
        bucket_name = bucket['Name']

        # Public access check
        try:
            policy_status = s3.get_bucket_policy_status(Bucket=bucket_name)
            if policy_status['PolicyStatus']['IsPublic']:
                public_buckets.append(bucket_name)
        except Exception:
            pass  # no policy

        # Encryption check
        try:
            s3.get_bucket_encryption(Bucket=bucket_name)
        except Exception:
            unencrypted_buckets.append(bucket_name)

    report['s3'] = {
        "public_buckets": public_buckets,
        "unencrypted_buckets": unencrypted_buckets
    }

    ### 3. Save Report ###
    if not dry_run:
        with open('reports/security_report.json', 'w') as f:
            json.dump(report, f, indent=2)

    return report
