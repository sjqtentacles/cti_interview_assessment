import boto3
import json
import geoip2.database
import user_agents
import argparse
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Table, Column, MetaData
from sqlalchemy.engine.url import URL
from sqlalchemy.dialects import mysql
from models import GeoIP, UserAgentLog

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
    return GeoIP(
        ip_addr=ip_str,
        latitude=output['Latitude'],
        longitude=output['Longitude'],
        postal=output['Zipcode'],
        city=output['City'],
        country=output['Country'],
        state=output['State']
    )

def parse_user_agent(ua_str):
    output = {}
    try:
        ua = user_agents.parse(ua_str)
        output['Browser'] = ua.browser.family
        output['OperatingSystem'] = ua.os.family
        output['DeviceType'] = ua.device.family
    except:
        pass
    return UserAgentLog(
            browser=output['Browser'],
            os=output['OperatingSystem'],
            device=output['DeviceType']
        )

def load_credentials(fname):
    with open(fname) as f:
        return json.loads(f.read())

def load_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--creds', 
        type=str, 
        help="AWS config file path, (default: 'aws.config.json')",
        default= 'aws.config.json')
    parser.add_argument('--geodb',
        type=str,
        help="Geo database file path, (default: 'GeoLite2-City.mmdb')",
        default= 'GeoLite2-City.mmdb')
    return parser

def load_mysql_engine(mysql_creds):
    SQLALCHEMY_DATABASE_URI = URL(**mysql_creds)
    return create_engine(SQLALCHEMY_DATABASE_URI, convert_unicode=True)

def initiate_tables(mysql_engine):
    GeoIP.metadata.create_all(mysql_engine)
    UserAgentLog.metadata.create_all(mysql_engine)

if __name__=='__main__':
    args = load_parser().parse_args()

    aws_creds = load_credentials(args.creds)
    mysql_creds = load_credentials('db.config.json')

    session = boto3.Session(
        aws_access_key_id = aws_creds['access_key'],
        aws_secret_access_key = aws_creds['secret']
    )
    s3 = session.resource('s3')
    bucket = s3.Bucket(aws_creds['bucket'])

    filelog_meta = bucket.Object(aws_creds['object_key']).get()
    filelog = filelog_meta['Body'].read().decode('utf-8')
    lines = filter(lambda x: len(x)>0, filelog.split('\n'))

    # I found a free database on maxmind website for geoip2 python package
    geodb_reader = geoip2.database.Reader(args.geodb)

    mysqlDB = load_mysql_engine(mysql_creds)
    initiate_tables(mysqlDB)
    
    Session = sessionmaker(bind=mysqlDB)
    session = Session()

    to_commit = []

    for line in lines:
        useragent_obj = parse_user_agent(line)
        geoip_obj = ip_to_geo(line.split()[0], geodb_reader)
        to_commit.append(useragent_obj)
        to_commit.append(geoip_obj)

    session.add_all(to_commit)    
    session.commit()
    session.close()