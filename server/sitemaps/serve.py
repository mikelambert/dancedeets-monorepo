from google.cloud import storage
import logging
from lxml import etree
import os.path

# local
import app
import base_servlet


client = storage.Client('dancedeets-hrd')
MapReduceShards = 16

def list_gcs_directories(bucket, prefix):
    # from https://github.com/GoogleCloudPlatform/google-cloud-python/issues/920
    iterator = bucket.list_blobs(prefix=prefix, delimiter='/')
    prefixes = set()
    for page in iterator.pages:
        prefixes.update(page.prefixes)
    return prefixes


def get_newest_path(bucket, mapreduce_name):
    dirs = list_gcs_directories(bucket, '%s/' % mapreduce_name)
    for dir in sorted(dirs):
        blobs = list(bucket.list_blobs(prefix=dir, delimiter='/'))
        if len(blobs) == MapReduceShards:
            return dir
    return None


def get_mapreduce_date(bucket, mapreduce_name):
    path = '%soutput-0' % get_newest_path(bucket, mapreduce_name)
    blob = bucket.get_blob(path)
    return blob.updated


def get_sitemap_for_mapreduce(mapreduce_name):
    bucket_name = 'dancedeets-hrd.appspot.com'
    bucket = client.get_bucket(bucket_name)
    path = get_newest_path(bucket, mapreduce_name)
    if not path:
        return None
    blobs = list(bucket.list_blobs(prefix=path, delimiter='/'))
    logging.info('Found these files: %s', [x.path for x in blobs])

    url_nodes = []
    for blob in blobs:
        blob_data = blob.download_as_string()
        url_nodes.append(blob_data)
    return sitemap_wrapper('\n'.join(url_nodes))



def sitemap_wrapper(url_nodes):
    return '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
%s
</urlset>
''' % url_nodes


@app.route('/sitemaps/recent.xml')
class RecentSitemapHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get(self):
        sitemap_data = get_sitemap_for_mapreduce('Generate FUTURE Sitemaps')
        if not sitemap_data:
            self.response.set_status(404)
            return
        self.response.headers["Content-Type"] = "text/xml"
        self.response.out.write(sitemap_data)


@app.route('/sitemaps/(\d+)-(\d+).xml')
class NumberedSitemapHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get(self, version, index):
        bucket_name = 'dancedeets-hrd.appspot.com'
        mapreduce_name = 'Generate Sitemaps'
        path = '%s/%s/output-%s' % (mapreduce_name, version, index)
        path = path.replace('../', '') # Maybe use its own bucket?
        bucket = client.get_bucket(bucket_name)
        blob = bucket.get_blob(path)
        if not blob:
            self.response.set_status(404)
            return
        blob_data = blob.download_as_string()
        xml = sitemap_wrapper(blob_data)
        self.response.headers["Content-Type"] = "text/xml"
        self.response.out.write(xml)


def sitemap_node(name, date):
    sitemap_node = etree.Element('sitemap')
    loc_node = etree.Element('loc')
    loc_node.text = 'https://www.dancedeets.com/sitemaps/%s.xml' % name
    sitemap_node.append(loc_node)
    if date:
        lastmod_node = etree.Element('lastmod')
        lastmod_node.text = date.strftime('%Y-%m-%dT%H:%M:%S')
        sitemap_node.append(lastmod_node)
    return sitemap_node


@app.route('/sitemaps/index.xml')
class SitemapMapHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get(self):
        root = etree.Element('sitemapindex')
        root.attrib['xmlns'] = 'http://www.sitemaps.org/schemas/sitemap/0.9'

        bucket_name = 'dancedeets-hrd.appspot.com'
        bucket = client.get_bucket(bucket_name)

        recent_date = get_mapreduce_date(bucket, 'Generate FUTURE Sitemaps')
        root.append(sitemap_node('recent', recent_date))

        versioned_date = get_mapreduce_date(bucket, 'Generate Sitemaps')
        path = get_newest_path(bucket, 'Generate Sitemaps')
        version = os.path.basename(path.strip('/'))
        print path, version
        for i in range(MapReduceShards):
            root.append(sitemap_node('%s-%s' % (version, i), versioned_date))

        root_data = etree.tostring(root, pretty_print=True)

        self.response.headers["Content-Type"] = "text/xml"
        self.response.out.write(root_data)
