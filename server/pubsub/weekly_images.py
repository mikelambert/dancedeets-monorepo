import datetime
from PIL import Image
from PIL import ImageFilter
import StringIO
import urllib

import app
import base_servlet
from rankings import cities

def openUrl(url):
    return Image.open(StringIO.StringIO(urllib.urlopen(url).read()))

full_size = (626, 840)

@app.route('/weekly/image')
class WeeklyImageHandler(base_servlet.BareBaseRequestHandler):
    def get(self):
        city = self.request.get('city')
        city = cities.City.get_by_key_name(city)
        d = datetime.date.today()
        week_start = d - datetime.timedelta(days=d.weekday()) # round down to last monday

        from . import weekly
        results = weekly._generate_results_for(city, week_start)
        images = [self.generate_image(x.db_event) for x in results]

        out_image = StringIO.StringIO()
        images[0].save(out_image, format='gif', save_all=True, append_images=images[1:], duration=2500)
        out_image.seek(0)
        self.response.headers['Content-Type'] = "image/gif"
        self.response.out.write(out_image.getvalue())
        out_image.close()


    def generate_image(self, event):
        im = openUrl('http://img.dancedeets.com/events/image_proxy/%s' % event.id)
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
