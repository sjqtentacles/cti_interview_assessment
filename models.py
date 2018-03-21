from sqlalchemy import Column
from sqlalchemy import String, Text, BigInteger, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class GeoIP(Base):
    __tablename__ = "geo_ip"

    id = Column(BigInteger, primary_key = True)
    ip_addr = Column(String(20))
    latitude = Column(Float)
    longitude = Column(Float)
    country = Column(String(50))
    state = Column(String(50))
    city = Column(String(50))
    postal = Column(String(10))

    def __repr__(self):
        return "<GeoIP %s %s>" % (self.ip_addr, self.country)

class UserAgentLog(Base):
    __tablename__ = "useragent_logs"

    id = Column(BigInteger, primary_key=True)
    browser = Column(String(50))
    os = Column('operating_system', String(50))
    device = Column('device_type', String(50))

    def __repr__(self):
        return "<UserAgentLog %s %s %s>" % (self.browser, self.os, self.device)