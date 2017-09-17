from dancedeets.loc import formatting


def get_address_from_geocode(geocode):
    if not geocode:
        return {}
    country = geocode.country(long=True)
    address = {}
    if country:
        address['country'] = country
    city = formatting.get_city(geocode)
    if city:
        address['city'] = city
    state = formatting.get_state(geocode)
    if state:
        address['state'] = state
    return address
