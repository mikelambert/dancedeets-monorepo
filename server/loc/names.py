import pycountry


def get_country_name(country_code):
    try:
        full_country = pycountry.countries.get(alpha_2=country_code).name
        return full_country.split(',')[0]
    except KeyError:
        return country_code
