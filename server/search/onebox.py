
SouthAfrica = {
    'South Africa Events & Sesssions: Rocka-Fella': 'http://rocka-fella.com/find-bboying-breaking-events-in-south-africa-and-africa/'
}

ONEBOX_DATA = {
    (40.7029741, -74.2598655): {
        'NYC Studio Classes': 'https://www.dancedeets.com/classes/nyc',
        'NYC Wiki Info': 'http://dance-wiki.appspot.com/New_York',
    },
    (34.0201812, -118.6919122): {
        'Los Angeles Studio Classes': 'https://www.dancedeets.com/classes/la',
        'Los Angeles Wiki Info': 'http://dance-wiki.appspot.com/Los_Angeles',
    },
    (1.3147298, 103.7769793): {
        'Singapore Blog: Dance Meets': 'http://www.dancemeets.com/',
    },
    # Pretoria
    (-27.7426843, 25.9248568): SouthAfrica,
    # Cape Town
    (-33.9144804, 18.375196): SouthAfrica,
}


def get_links_for_query(query):
    onebox_links = {}

    if not query.bounds:
        # This will happen on location-less searches (worldwide)
        return onebox_links

    # We try to keep searches as simple as possible,
    # using just AND queries on latitude/longitude.
    # But for stuff crossing +/-180 degrees,
    # we need to do an OR longitude query on each side.
    search_latitudes = (query.bounds[0][0], query.bounds[1][0])
    search_longitudes = (query.bounds[0][1], query.bounds[1][1])

    for (latitude, longitude), links in ONEBOX_DATA.iteritems():
        good_latitude = latitude >= search_latitudes[0] and latitude <= search_latitudes[1]
        if search_longitudes[0] < search_longitudes[1]:
            good_longitude = longitude >= search_longitudes[0] and longitude <= search_longitudes[1]
        else:
            good_longitude = longitude >= search_longitudes[0] or longitude <= search_longitudes[1]
        if good_latitude and good_longitude:
            onebox_links.update(links)
    return [{'title': x, 'url': onebox_links[x]} for x in sorted(onebox_links)]
