
from PIL import Image
import StringIO
import urllib

def openUrl(url):
    return Image.open(StringIO.StringIO(urllib.urlopen(url).read()))

event_ids = [
    '1686119861688541',
    'enter-the-stage:NC8xOTMy',
    '105297496678155',
]
full_size = (626, 840)
images = [openUrl('http://img.dancedeets.com/events/image_proxy/%s' % x) for x in event_ids]
fit_images = []
for im in images:
    image_size = (im.width, im.height)
    scale = tuple(1.0 * x / y for x, y in zip(full_size, image_size))
    min_scale = min(scale)
    image_new_size = tuple(int(round(min_scale * x)) for x in image_size)
    resized = im.resize(image_new_size, resample=Image.BICUBIC)

    offset = tuple((x - y) / 2 for x, y in zip(full_size, image_new_size))
    target = Image.new('RGBA', full_size)
    target.paste(resized, offset)
    fit_images.append(target)

fit_images[0].save('./test.gif', save_all=True, append_images=fit_images[1:], duration=2000)
#vv.imshow(im)
