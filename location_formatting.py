
def get_formatting_parts(geocode):
    address_components = geocode.address_components()

    def get_component(name, long=True):
        components = [x[long and 'long_name' or 'short_name'] for x in address_components if name in x['types']]
        if components:
            return components[0]
        else:
            return None

    colloquial_area = get_component('colloquial_area')
    if colloquial_area:
        address_components = [x for x in address_components if 'colloquial_area' not in x['types']]

    components = [
        colloquial_area,
        get_component('neighborhood'),
        get_component('sublocality'),
        get_component('locality'),
    ]
    country = get_component('country')
    if country in ['United States', 'Canada', 'Australia', 'Mexico', 'Malaysia', 'Japan', 'Hong Kong']:
        components.extend([
            get_component('administrative_area_level_1', long=False),
        ])
    components.extend([
        get_component('country'),
    ])
    return [x for x in components if x]

def format_address(geocode):
    return _format_from_parts(get_formatting_parts(geocode))

def _format_from_parts(parts):
    return ', '.join(parts)

def format_addresses(parts_list):
    min_length = min(len(x) for x in parts_list)
    # If all our addresses are in the same country, or state, then trim that off as irrelevant
    for i in range(min_length-1    ):
        #print i, parts_list
        index_parts = set([x[-1] for x in parts_list])
        # If they all map to the same thing, let's trim it off
        if len(index_parts) == 1:
            for x in parts_list:
                if len(x) > 1:
                    x.pop()
    #print parts_list
    # Now grab the last two pieces of data, as being relevant to where we are.
    # Anything earlier than that in the list, is too specific at the scale we are currently at.
    parts_list = [x[-2:] for x in parts_list]
    parts_list = [_format_from_parts(x) for x in parts_list]
    return parts_list
