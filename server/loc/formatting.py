
def get_city(geocode):
    country = geocode.get_component('country', long=False)
    if not country:
        return geocode.get_component('administrative_area_level_2')
    elif country in ['US', 'CA', 'AU', 'MX', 'MY', 'ID', 'JP', 'HK', 'TW']:
        return geocode.get_component('locality')
    else:
        return geocode.get_component('locality')

def get_state(geocode):
    country = geocode.get_component('country', long=False)
    if not country:
        return geocode.get_component('administrative_area_level_1')
    elif country in ['US', 'CA', 'AU', 'MX', 'MY', 'ID', 'JP', 'HK', 'TW']:
        return geocode.get_component('administrative_area_level_1', long=False) or geocode.get_component('administrative_area_level_2', long=False)
    else:
        return ''

def _get_formatting_parts(geocode, include_neighborhood):
    if not geocode:
        return []
    geocode = geocode.copy()

    components = [
        geocode.get_component('neighborhood') if include_neighborhood else None,
        geocode.get_component('sublocality'),
    ]
    country = geocode.get_component('country', long=False)
    if not country:
        components.extend([
            geocode.get_component('administrative_area_level_2'),
            geocode.get_component('administrative_area_level_1'),
        ])
    elif country in ['US', 'CA', 'AU', 'MX', 'MY', 'ID', 'JP', 'HK', 'TW']:
        mini_components = [
            geocode.get_component('locality'),
            geocode.get_component('administrative_area_level_1', long=False) or geocode.get_component('administrative_area_level_2', long=False),
            ]
        components.append(', '.join(x for x in mini_components if x))
    else:
        if geocode.get_component('postal_town') or geocode.get_component('locality'):
            # In the UK, they don't use locality, but do use postal_town. So let's grab the postal_town for display here
            components.extend([
                geocode.get_component('postal_town'),
                geocode.get_component('locality'),
            ])
        else:
            # In Columbia on event 1436024073115860, there is no locality/postal_town, but is an administrative_area_level_2
            # So let's try to use and display that, to avoid "Columbia" address
            components.extend([
                geocode.get_component('administrative_area_level_2'),
            ])
    components.extend([
        geocode.get_component('country'),
    ])
    geocode.delete_component('neighborhood')
    geocode.delete_component('sublocality')
    geocode.delete_component('locality')
    geocode.delete_component('administrative_area_level_1')
    geocode.delete_component('country')
    components = [
        geocode.get_component('colloquial_area'),
    ] + components + [
        geocode.get_component('continent'),
    ]

    return [x for x in components if x]

def _format_from_parts(parts):
    return ', '.join(parts)

def format_geocode(geocode, include_neighborhood=False):
    return _format_from_parts(_get_formatting_parts(geocode, include_neighborhood=include_neighborhood))

def format_geocodes(geocodes, include_neighborhood=False):
    if geocodes == []:
        return []
    parts_list = [_get_formatting_parts(geocode, include_neighborhood=include_neighborhood) for geocode in geocodes]
    min_length = min(len(x) for x in parts_list)
    # If all our addresses are in the same country, or state, then trim that off as irrelevant
    for i in range(min_length-1):
        # Get the set of the 'last' element of each of our addresses
        index_parts = set([x[-1] for x in parts_list])
        # If they all are the same thing, let's trim it off as unnecessary
        if len(index_parts) == 1:
            for x in parts_list:
                x.pop()
    # Now grab the last two pieces of data, as being relevant to where we are.
    # Anything earlier than that in the list, is too specific at the scale we are currently at.
    parts_list = [x[-2:] for x in parts_list]
    addresses_list = [_format_from_parts(x) for x in parts_list]
    return addresses_list
