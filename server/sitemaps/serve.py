from google.cloud import storage
import logging
from lxml import etree
import os.path

# local
import app
import base_servlet


def generate_urlset(url_nodes):
    urlset_node = etree.Element('urlset')
    urlset_node.attrib['xmlns'] = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    for url_node in url_nodes:
        urlset_node.append(url_node)
    return urlset_node


client = storage.Client('dancedeets-hrd')


def list_gcs_directories(bucket, prefix):
    # from https://github.com/GoogleCloudPlatform/google-cloud-python/issues/920
    iterator = bucket.list_blobs(prefix=prefix, delimiter='/')
    prefixes = set()
    for page in iterator.pages:
        print page, page.prefixes
        prefixes.update(page.prefixes)
    return prefixes

def get_newest_path(bucket, mapreduce_name):
    dirs = list_gcs_directories(bucket, '%s/' % mapreduce_name)
    newest = sorted(dirs)[0]
    return newest


def get_sitemap_for_mapreduce(mapreduce_name):
    bucket_name = 'dancedeets-hrd.appspot.com'
    bucket = client.get_bucket(bucket_name)
    path = get_newest_path(bucket, mapreduce_name)
    blobs = list(bucket.list_blobs(prefix=path, delimiter='/'))
    logging.info('Found these files: %s', [x.path for x in blobs])
    url_nodes = []
    for blob in blobs:
        url_node_strings = blob.download_as_string().split('\n')
        url_nodes.extend(etree.fromstring(x) for x in url_node_strings)

    urlset_node = generate_urlset(url_nodes)
    return etree.tostring(urlset_node, pretty_print=True)


@app.route('/sitemaps/recent.xml')
class ReloadEventsHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.response.headers["Content-Type"] = "text/xml"
        sitemap_data = get_sitemap_for_mapreduce('Generate FUTURE Sitemaps')
        self.response.out.write(sitemap_data)
