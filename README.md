# CTI Python interview assessment

How to get it running
*****

* [Download this free geoip database (about 60MB)](http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.tar.gz) 
	
* Extract the mmdb file from the above download and put it in the local directory of `main.py`

* Add credentials found in the assessment prompt's PDF to the sample aws.config file and rename it to 'aws.config.json'

* Start a new virtualenv and install the packages from requirements.txt (assuming python 2.7)

* Install MySQL locally (I used version 5.7)

* Setup a local mysql db user "ctiuser" with pass "ctipass" and a database named "cti" to keep it simple. These credentials are already put in `db.config.json` so you can change it if necessary, but again, just for simplicity. Normally the file would be put into gitignore, but doesn't matter for this project. 