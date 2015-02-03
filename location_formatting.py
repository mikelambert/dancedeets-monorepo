
def get_formatting_parts(gmaps_data):
    address_components = gmaps_data['address_components']

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

def format_address(gmaps_data):
    return ', '.join(get_formatting_parts(gmaps_data))

