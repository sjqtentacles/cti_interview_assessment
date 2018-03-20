import boto3
import json
import geoip2.database
from user_agents import parse
import argparse

def ip_to_geo(ip_str, geo_reader):
    output = {}
    try:
        response = geo_reader.city(ip_str)
        output['Latitude'] = response.location.latitude
        output['Longitude'] = response.location.longitude
        output['Zipcode'] = response.postal.code
        output['City'] = response.city.name
        output['Country'] = response.country.name
        output['State'] = response.subdivisions.most_specific.name
    except:
        pass
    return output

def parse_user_agent(ua_str):
    output = {}
    try:
        user_agent = parse(ua_str)
        output['Browser'] = user_agent.browser.family
        output['OperatingSystem'] = user_agent.os.family
        output['DeviceType'] = user_agent.device.family
    except:
        pass
    return output

if __name__=='__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--creds', 
        type=str, 
        help="AWS config file path, (default: 'aws.config.json')",
        default= 'aws.config.json')
    parser.add_argument('--geodb',
        type=str,
        help="Geo database file path, (default: 'GeoLite2-City.mmdb')",
        default= 'GeoLite2-City.mmdb')

    args = parser.parse_args()

    creds = {}
    with open(args.creds) as f:
        creds = json.loads(f.read())

    session = boto3.Session(
        aws_access_key_id = creds['access_key'],
        aws_secret_access_key = creds['secret']
    )

    s3 = session.resource('s3')
    bucket = s3.Bucket(creds['bucket'])

    filelog_meta = bucket.Object(creds['object_key']).get()
    filelog = filelog_meta['Body'].read().decode('utf-8')

    lines = filelog.split('\n')
    # I found a free database on maxmind website for geoip2 python package
    geodb_reader = geoip2.database.Reader(args.geodb)

    for line in lines[0:10]:
        ip_addr = line.split()[0]
        print ip_to_geo(ip_addr, geodb_reader)
        print parse_user_agent(line)