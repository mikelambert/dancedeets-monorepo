import csv
import datetime
import os

GEONAMES_PATH = '/Users/lambert/Dropbox/dancedeets/data/geonames/'

class GeonamesDialect(csv.Dialect):
    quoting = csv.QUOTE_NONE
    delimiter = '\t'
    lineterminator = '\n'

class Geoname(object):
    __slots__ = ['geonameid', 'name', 'asciiname', 'alternatenames', 'latitude', 'longitude', 'feature_class', 'feature_code', 'country_code', 'cc2', 'admin1_code', 'admin2_code', 'admin3_code', 'admin4_code', 'population', 'elevation', 'gtopo30', 'timezone', 'modification_date']

    def __init__(self, kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

def geo_open(filename):
    full_geonames_path = os.path.join(GEONAMES_PATH, filename)
    print full_geonames_path
    for row in csv.reader(open(full_geonames_path), dialect=GeonamesDialect):
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]

def cities(min_population=5000):
    assert min_population in [1000, 5000, 15000]
    for row in geo_open('cities%s.txt' % min_population):
        geoname = Geoname(dict(zip(Geoname.__slots__, row)))
        geoname.geonameid = int(geoname.geonameid)
        geoname.alternatenames = geoname.alternatenames.split(',')
        geoname.latitude = float(geoname.latitude)
        geoname.longitude = float(geoname.longitude)
        geoname.cc2 = geoname.cc2.split(',')
        geoname.population = int(geoname.population)
        geoname.elevation = int(geoname.elevation) if geoname.elevation else None
        geoname.modification_date = datetime.datetime.strptime(geoname.modification_date, '%Y-%m-%d').date()

        yield geoname
