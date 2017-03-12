import pycountry

def get_country_name(country_code):
    try:
        full_country = pycountry.countries.get(alpha_2=country_code).name
    except:
        full_country = country_code
    return full_country.split(',')[0]
