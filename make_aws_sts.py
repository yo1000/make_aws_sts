def get_or_else(v, f):
    if v:
        return v
    else:
        return f()

# main
import os
import configparser
import boto3
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--profile', help='Profile name')
parser.add_argument('-a', '--account', help='Account id')
parser.add_argument('-u', '--username', help='Username')
parser.add_argument('-t', '--token', help='Token code')
args = parser.parse_args()

profile = get_or_else(args.profile, lambda: input('Profile name: '))
account = get_or_else(args.account, lambda: input('Account id: '))
username = get_or_else(args.username, lambda: input('Username: '))
token_code = get_or_else(args.token, lambda: input('Token code: '))

path_home = os.path.expanduser('~')
path_credentials = '{home}/.aws/credentials'.format(home=path_home)

config = configparser.ConfigParser()
config.read(path_credentials)

AWS_ACCESS_KEY_ID = 'aws_access_key_id'
AWS_SECRET_ACCESS_KEY = 'aws_secret_access_key'

# Check profile and required keys
if (profile not in config):
    print('Error: Profie [{profile}] is not exists'.format(profile=profile), file=sys.stderr)
    sys.exit(1)
if (AWS_ACCESS_KEY_ID not in config[profile]):
    print('Error: {aws_access_key_id} is not configured in [{profile}] profile'.format(aws_access_key_id=AWS_ACCESS_KEY_ID, profile=profile), file=sys.stderr)
    sys.exit(1)
if (AWS_SECRET_ACCESS_KEY not in config[profile]):
    print('Error: {aws_secret_access_key} is not configured in [{profile}] profile'.format(aws_secret_access_key=AWS_SECRET_ACCESS_KEY, profile=profile), file=sys.stderr)
    sys.exit(1)

aws_access_key_id = config[profile][AWS_ACCESS_KEY_ID]
aws_secret_access_key = config[profile][AWS_SECRET_ACCESS_KEY]

serial_number='arn:aws:iam::{account}:mfa/{username}'.format(account=account, username=username)

client = boto3.client(
    'sts',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key)

response = client.get_session_token(
    DurationSeconds=3600,
    SerialNumber=serial_number,
    TokenCode=token_code
)

profile_sts = '{profile}_sts'.format(profile=profile)
config[profile_sts] = {}
config[profile_sts][AWS_ACCESS_KEY_ID] = response['Credentials']['AccessKeyId']
config[profile_sts][AWS_SECRET_ACCESS_KEY] = response['Credentials']['SecretAccessKey']
config[profile_sts]['aws_session_token'] = response['Credentials']['SessionToken']

with open(path_credentials, 'w') as configfile:
    config.write(configfile)

print('STS Credential was saved as [{profile}] profile to {file}'.format(profile=profile_sts, file=path_credentials))
