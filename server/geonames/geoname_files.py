import csv
import datetime
import os

GEONAMES_PATH = '/Users/lambert/Dropbox/dancedeets/data/geonames/'

class GeonamesDialect(csv.Dialect):
    quoting = csv.QUOTE_NONE
    delimiter = '\t'
    lineterminator = '\n'

class Slotted(object):
    def __init__(self, kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

class Geoname(Slotted):
    __slots__ = ['geonameid', 'name', 'asciiname', 'alternatenames', 'latitude', 'longitude', 'feature_class', 'feature_code', 'country_code', 'cc2', 'admin1_code', 'admin2_code', 'admin3_code', 'admin4_code', 'population', 'elevation', 'gtopo30', 'timezone', 'modification_date']

    def __init__(self, kwargs):
        super(Geoname, self).__init__(kwargs)
        self.geonameid = int(self.geonameid)
        self.alternatenames = self.alternatenames.split(',')
        self.latitude = float(self.latitude)
        self.longitude = float(self.longitude)
        self.cc2 = self.cc2.split(',')
        self.population = int(self.population)
        self.elevation = int(self.elevation) if self.elevation else None
        self.modification_date = datetime.datetime.strptime(self.modification_date, '%Y-%m-%d').date()

class Country(Slotted):
    __slots__ = ['iso', 'iso3', 'iso_numeric', 'fips', 'name', 'capital', 'area', 'population', 'continent', 'tld', 'currency_code', 'currency_name', 'phone', 'postal_code_format', 'postal_code_regex', 'languages', 'geonameid']

    def __init__(self, kwargs):
        super(Geoname, self).__init__(kwargs)
        self.iso_numeric = int(self.iso_numeric)
        self.area = int(self.area)
        self.population = int(self.population)
        self.geonameid = int(self.geonameid)

class AlternateName(Slotted):
    __slots__ = ['alternateNameId', 'geonameid', 'isolanguage', 'alternateName', 'isPreferredName', 'isShortName', 'isColloquial', 'isHistoric']

    def __init__(self, kwargs):
        super(Geoname, self).__init__(kwargs)
        self.alternateNameId = int(self.alternateNameId)
        self.geonameid = int(self.geonameid)

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

        yield geoname

def countries():
    for row in geo_open('countryInfo.txt'):
        geoname = Country(dict(zip(Country.__slots__, row)))
        yield geoname

def alternateNames():
    for row in geo_open('alternateNames.txt'):
        geoname = AlternateName(dict(zip(AlternateName.__slots__, row)))
        yield geoname
