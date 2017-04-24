import datetime
import logging
from PIL import Image
from PIL import ImageFilter
import subprocess
import StringIO
import tempfile

import app
import base_servlet
from events import event_image
from rankings import cities
from util import gcs
from util import runtime

full_size = (626, 840)

WEEKLY_IMAGE_BUCKET = 'dancedeets-weekly'

def build_animated_image(results):
    images = [_generate_image(x.db_event) for x in results]

    out_image = StringIO.StringIO()
    images[0].save(out_image, format='gif', save_all=True, append_images=images[1:], duration=2500)
    out_image.seek(0)
    image_data = out_image.getvalue()
    out_image.close()

    image_data = _compress_image(image_data)
    return image_data

def _compress_image(image_data):
    if subprocess.call('which gifsicle > /dev/null', shell=True):
        logging.warning('Could not find gifsicle in path')
        return image_data
    orig = tempfile.NamedTemporaryFile()
    orig.write(image_data)
    orig.flush()
    compressed = tempfile.NamedTemporaryFile()

    subprocess.call('gifsicle -O3 -o %s %s' % (compressed.name, orig.name), shell=True)

    compressed_data = compressed.read()
    compressed.close()
    logging.info('Compressed %s -> %s bytes', len(image_data), len(compressed_data))
    orig.close()
    return compressed_data

def _generate_image(event):
    image_data = event_image.get_image(event)
    im = Image.open(StringIO.StringIO(image_data))
    image_size = (im.width, im.height)
    scale = tuple(1.0 * x / y for x, y in zip(full_size, image_size))

    # Generate the background-image that is blurred and backgrounds the main image
    max_scale = max(scale)
    background_image_new_size = tuple(int(round(max_scale * x)) for x in image_size)
    background_resized = im.resize(background_image_new_size, resample=Image.BICUBIC)
    background_blurred = background_resized.filter(ImageFilter.GaussianBlur(100))
    background_offset = tuple((x - y) / 2 for x, y in zip(full_size, background_image_new_size))

    # Generate the scaled-image that fits the frame exactly
    min_scale = min(scale)
    foreground_image_size = tuple(int(round(min_scale * x)) for x in image_size)
    foreground_resized = im.resize(foreground_image_size, resample=Image.BICUBIC)
    foreground_offset = tuple((x - y) / 2 for x, y in zip(full_size, foreground_image_size))

    target = Image.new('RGB', full_size)
    target.paste(background_blurred, background_offset)
    target.paste(foreground_resized, foreground_offset)

    return target

def _generate_path(city, week_start):
    path = '%s/%s.gif' % (week_start.strftime('%Y-%m-%d'), city.display_name())
    if runtime.is_local_appengine():
        path = 'dev/%s' % path
    return path

def build_and_cache_image(city, week_start, search_results):
    image = build_animated_image(search_results)
    path = _generate_path(city, week_start)
    gcs.put_object(WEEKLY_IMAGE_BUCKET, path, image)
    image_url = 'http://www.dancedeets.com/weekly/image?city=%s&week_start=%s' % (city.key().name(), week_start.strftime('%Y-%m-%d'))
    return image_url

def load_cached_image(city, week_start):
    path = _generate_path(city, week_start)
    logging.info('Looking up image at %s: %s', WEEKLY_IMAGE_BUCKET, path)
    try:
        image_data = gcs.get_object(WEEKLY_IMAGE_BUCKET, path)
    except gcs.NotFoundError:
        image_data = None
    return image_data

@app.route('/weekly/image')
class WeeklyImageHandler(base_servlet.BareBaseRequestHandler):
    def get(self):
        city_name = self.request.get('city')
        city = cities.City.get_by_key_name(city_name)

        disable_cache = self.request.get('disable_cache') == '1'
        if self.request.get('week_start'):
            week_start = datetime.datetime.strptime(self.request.get('week_start'), '%Y-%m-%d').date()
        else:
            d = datetime.date.today()
            week_start = d - datetime.timedelta(days=d.weekday()) # round down to last monday

        image_data = not disable_cache and load_cached_image(city, week_start)

        if not image_data:
            logging.error('Failed to find image for week %s in city %s, dynamically generating...', week_start, city)
            from . import weekly
            results = weekly._generate_results_for(city, week_start)
            image_data = build_animated_image(results)
        self.response.headers['Content-Type'] = "image/gif"
        self.response.out.write(image_data)
