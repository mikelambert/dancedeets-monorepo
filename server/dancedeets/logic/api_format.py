import datetime
import logging
from slugify import slugify

from dancedeets import event_types
from dancedeets.events import eventdata
from dancedeets.events import featured
from dancedeets.loc import address
from dancedeets.loc import gmaps_api
from dancedeets.loc import math
from dancedeets.event_attendees import popular_people
from dancedeets.rankings import cities_db
from dancedeets.search import onebox
from dancedeets.search import search_base
from dancedeets.util import language
from dancedeets.util import urls

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
DATETIME_FORMAT_TZ = "%Y-%m-%dT%H:%M:%S%z"


def canonicalize_search_event_data(result, version):
    event_api = {}
    event_api['id'] = result.event_id
    event_api['name'] = result.data['name']
    event_api['slugged_name'] = slugify(unicode(result.data['name']))
    event_api['start_time'] = result.data['start_time']
    event_api['end_time'] = result.data['end_time']

    geocode = None
    if result.data['lng'] and result.data['lat']:
        geocode = {
            'longitude': result.data['lng'],
            'latitude': result.data['lat'],
        }
    event_api['venue'] = {
        'name': result.data.get('venue', {}).get('name', None),
        'geocode': geocode,
        'address': result.data.get('venue', {}).get('address', None),
    }
    if result.data.get('picture'):
        event_api['picture'] = {
            'source': urls.event_image_url(result.event_id),
            'width': result.data.get('picture', {}).get('width', 1),
            'height': result.data.get('picture', {}).get('height', 1),
        }
    else:
        event_api['picture'] = None

    annotations = {}
    annotations['keywords'] = result.data['keywords']
    annotations['categories'] = event_types.humanize_categories(result.data['categories'])
    event_api['annotations'] = annotations
    if result.data['attendee_count']:
        event_api['rsvp'] = {
            'attending_count': result.data['attendee_count'],
            'maybe_count': result.data.get('maybe_count', 0),
        }
    else:
        event_api['rsvp'] = None
    return event_api


def canonicalize_post_data(post, version):
    """
    post['created_time']
    post['updated_time']

    post['from']
        post['from']['id']
        post['from']['name']

    post['message']
        post['message_tags'][0]['id']
        post['message_tags'][0]['length']
        post['message_tags'][0]['offset']
        post['message_tags'][0]['name']
        post['message_tags'][0]['type']

    post['link']
    post['picture']
    post['name']
    """
    post_api = {}
    post_api['created_time'] = post['created_time']
    post_api['message'] = post['message']
    if 'link' in post:
        post_api['link'] = post['link']
    if 'from' in post:
        post_api['from'] = {
            'id': post['from']['id'],
            'name': post['from'].get('name', 'Unknown'),
        }
    else:
        logging.info('post without from: %s', post)
    return post_api


def canonicalize_base_event_data(db_event, version):
    event_api = {}
    event_api['id'] = db_event.id
    event_api['name'] = db_event.name
    event_api['slugged_name'] = slugify(unicode(db_event.name))
    event_api['start_time'] = db_event.start_time_with_tz.strftime(DATETIME_FORMAT_TZ)
    # end time can be optional, especially on single-day events that are whole-day events
    if db_event.end_time_with_tz:
        event_api['end_time'] = db_event.end_time_with_tz.strftime(DATETIME_FORMAT_TZ)
    else:
        event_api['end_time'] = None

    event_api['extraImageCount'] = len(db_event.extra_image_urls())

    # cover images
    if db_event.has_image:
        if version >= (1, 3):
            if db_event.json_props:
                width = db_event.json_props['photo_width']
                height = db_event.json_props['photo_height']
            else:
                cover = db_event.largest_cover
                width = cover['width']
                height = cover['height']
            # Used by new react builds
            event_api['picture'] = {
                'source': urls.event_image_url(db_event.id),
                'width': width,
                'height': height,
            }
        else:
            if db_event.json_props:
                ratio = 1.0 * db_event.json_props['photo_width'] / db_event.json_props['photo_height']
            else:
                cover = db_event.cover_images[0]
                ratio = 1.0 * cover['width'] / cover['height']
            # Covers the most common screen sizes, according to Mixpanel:
            widths = reversed([320, 480, 720, 1080, 1440])
            cover_images = [{
                'source': urls.event_image_url(db_event.id, width=width),
                'width': width,
                'height': int(width / ratio)
            } for width in widths]

            # Used by old android and ios builds
            event_api['picture'] = urls.event_image_url(db_event.id, width=200, height=200)
            # Used by old react builds
            event_api['cover'] = {
                'cover_id': 'dummy',  # Android (v1.1) expects this value, even though it does nothing with it.
                'images': sorted(cover_images, key=lambda x: -x['height']),
            }
    else:
        event_api['picture'] = None
        event_api['cover'] = None

    # location data
    if db_event.location_name:
        venue_location_name = db_event.location_name
    else:
        # In these very rare cases (where we've manually set the location on a location-less event), return ''
        # TODO: We'd ideally like to return None, but unfortunately Android expects this to be non-null in 1.0.3 and earlier.
        venue_location_name = ""
    venue = db_event.venue
    if 'name' in venue and venue['name'] != venue_location_name:
        logging.error(
            "For event %s, venue name %r is different from location name %r", db_event.fb_event_id, venue['name'], venue_location_name
        )
    venue_id = db_event.venue_id
    address = None
    if 'country' in venue:
        address = {}
        for key in ['street', 'city', 'state', 'zip', 'country']:
            if key in venue:
                address[key] = venue.get(key)
        real_geocode = db_event.get_geocode()
        if real_geocode:
            address['countryCode'] = real_geocode.country()
        else:
            logging.warning('Event %s had country %s but no geocode', db_event.id, venue['country'])

    geocode = None
    if db_event.longitude and db_event.latitude:
        geocode = {
            'longitude': db_event.longitude,
            'latitude': db_event.latitude,
        }
    # I have seen:
    # - no venue subfields at all (ie, we manually specify the address/location in the event or remapping), which will be returned as "" here (see above comment)
    # - name only (possibly remapped?)
    # - name and id and geocode
    # - name and address and id and geocode
    # - name and address (everything except zip) and id and geocode
    # - so now address can be any subset of those fields that the venue author filled out...but will specify country, at least
    # ...are there more variations? write a mapreduce on recent events to check?
    event_api['venue'] = {
        'name': venue_location_name,
        'id': venue_id,
        'address': address,
        'geocode': geocode,
    }

    return event_api


def canonicalize_event_data(db_event, version, event_wall=None, event_keywords=None):
    event_api = canonicalize_base_event_data(db_event, version)
    event_api['description'] = db_event.description
    event_api['source'] = {
        'name': db_event.source_name,
        'url': db_event.source_url,
    }

    if db_event.json_props and 'language' in db_event.json_props:
        event_api['language'] = db_event.json_props['language']
    else:
        # bwcompat that let's this work without the need to re-save
        text = '%s. %s' % (event_api['name'], event_api['description'])
        try:
            event_api['language'] = language.detect(text)
        except ValueError:
            logging.exception('Error detecting language on event %s with text %r', db_event.id, text)
            event_api['language'] = None

    # people data
    event_api['admins'] = db_event.admins

    annotations = {}
    if db_event and db_event.creation_time:
        annotations['creation'] = {
            'time': db_event.creation_time.strftime(DATETIME_FORMAT),
            'method': db_event.creating_method,
        }
        if db_event.creating_method == eventdata.CM_USER:
            annotations['creation'].update({
                'creator': str(db_event.creating_fb_uid) if db_event.creating_fb_uid else None,  #STR_ID_MIGRATE
                'creatorName': db_event.creating_name if db_event.creating_name else None,  #STR_ID_MIGRATE
            })
    else:
        annotations['creation'] = None
    # We may have keywords from the search result that called us
    if event_keywords:
        annotations['dance_keywords'] = event_keywords
        annotations['categories'] = event_keywords
    # or from the db_event associated with this
    elif db_event:
        annotations['dance_keywords'] = db_event.event_keywords
    # or possibly none at all, if we only received a fb_event..
    else:
        pass
    if db_event:  # TODO: When is this not true?
        annotations['categories'] = event_types.humanize_categories(db_event.auto_categories)

    if event_wall and not event_wall['empty']:
        posts = event_wall['wall']['data']
        api_posts = [canonicalize_post_data(x, version) for x in posts if x.get('message')]
        event_api['posts'] = api_posts
    else:
        event_api['posts'] = []

    event_api['annotations'] = annotations
    event_api['ticket_uri'] = db_event.ticket_uri
    # maybe handle: 'timezone', 'updated_time'
    # rsvp_fields = ['attending_count', 'declined_count', 'maybe_count', 'noreply_count']
    if db_event.attending_count or db_event.maybe_count:
        event_api['rsvp'] = {
            'attending_count': db_event.attending_count or 0,
            'maybe_count': db_event.maybe_count or 0,
        }
    else:
        event_api['rsvp'] = None

    return event_api


def people_groupings(geocode, distance, skip_people):
    groupings = None
    if skip_people or not geocode:
        groupings = {}
    else:
        center_latlng, southwest, northeast = search_base.get_center_and_bounds(geocode, distance)
        if not center_latlng:
            # keyword-only search, no location to give promoters for
            logging.info('No center latlng, skipping person groupings')
        else:
            distance_km = math.get_inner_box_radius_km(southwest, northeast)
            if distance_km > 1000:
                logging.info('Search area >1000km, skipping person groupings')
                # Too big a search area, not worth showing promoters or dancers
            else:
                # TODO: Replace with a call to get_attendees_within (that also gets ADMIN people)
                southwest_baseline, northeast_baseline = math.expand_bounds((center_latlng, center_latlng), cities_db.NEARBY_DISTANCE_KM)
                distance_km_baseline = math.get_inner_box_radius_km(southwest_baseline, northeast_baseline)
                if distance_km < distance_km_baseline:
                    southwest = southwest_baseline
                    northeast = northeast_baseline
                logging.info('Searching for cities within %s', (southwest, northeast))
                included_cities = cities_db.get_contained_cities((southwest, northeast))
                biggest_cities = sorted(included_cities, key=lambda x: -x.population)[:10]
                geoname_ids = [city.geoname_id for city in biggest_cities]
                logging.info('City names: %s', [city.display_name() for city in biggest_cities])
                if geoname_ids:
                    try:
                        people_rankings = popular_people.get_people_rankings_for_city_names(geoname_ids)
                        groupings = popular_people.combine_rankings(people_rankings, max_people=10)
                    except:
                        logging.exception('Error creating combined people rankings')
                        groupings = {}
                    new_groupings = {
                        'ADMIN': {},
                        'ATTENDEE': {},
                    }
                    # These lists can get huge now...make sure we trim them down for what clients need!
                    for person_type, styles in groupings.iteritems():
                        for style in event_types.STYLES + ['']:
                            index_style_name = style.index_name if style else ''
                            public_style_name = style.public_name if style else ''
                            good_style = None
                            for style in styles:
                                style_name, city = style.split(': ', 2)
                                if popular_people.is_summed_area(city) and style_name == index_style_name:
                                    good_style = style
                            if good_style:
                                new_groupings[person_type][public_style_name] = styles[good_style][:10]
                    groupings = new_groupings

                    logging.info('Person Groupings:\n%s', '\n'.join('%s: %s' % kv for kv in groupings.iteritems()))
    return groupings


def build_search_results_api(form, search_query, search_results, version, need_full_event, geocode, distance, skip_people=False):
    if geocode:
        center_latlng, southwest, northeast = search_base.get_center_and_bounds(geocode, distance)
    else:
        center_latlng = None
        southwest = None
        northeast = None

    onebox_links = []
    if search_query:
        onebox_links = onebox.get_links_for_query(search_query)

    json_results = []
    for result in search_results:
        try:
            if need_full_event:
                json_result = canonicalize_event_data(result.db_event, version, event_keywords=result.event_keywords)
            else:
                json_result = canonicalize_search_event_data(result, version)
            json_results.append(json_result)
        except Exception as e:
            logging.exception("Error processing event %s: %s" % (result.event_id, e))

    real_featured_infos = []
    try:
        featured_infos = featured.get_featured_events_for(southwest, northeast)
        for featured_info in featured_infos:
            try:
                featured_info['event'] = canonicalize_event_data(featured_info['event'], version)
                real_featured_infos.append(featured_info)
            except Exception as e:
                logging.exception("Error processing event %s: %s" % (result.event_id, e))
    except Exception as e:
        logging.exception("Error building featured event listing: %s", e)

    groupings = people_groupings(geocode, distance, skip_people=skip_people)
    query = {}
    if form:
        for field in form:
            query[field.name] = getattr(field, '_value', lambda: field.data)()

    if geocode:
        address_geocode = gmaps_api.lookup_address(geocode.formatted_address())
    else:
        address_geocode = None

    json_response = {
        'results': json_results,
        'onebox_links': onebox_links,
        'location': geocode.formatted_address() if geocode else None,
        'address': address.get_address_from_geocode(address_geocode),
        'query': query,
    }
    if groupings is not None:
        json_response['people'] = groupings
    if version <= (1, 3):
        json_response['featured'] = [x['event'] for x in real_featured_infos]
    else:
        json_response['featuredInfos'] = real_featured_infos
    if southwest and northeast:
        json_response['location_box'] = {
            'southwest': {
                'latitude': southwest[0],
                'longitude': southwest[1],
            },
            'northeast': {
                'latitude': northeast[0],
                'longitude': northeast[1],
            },
        }
    return json_response
