from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time

geolocator = Nominatim(user_agent="geo_app_finder_project")

def get_coordinates(venue_name, province_name):
    if not venue_name:
        return None, None
    search_query = f"{venue_name}, {province_name}, Thailand"
    try:
        time.sleep(1)
        location = geolocator.geocode(search_query, timeout=10)
        
        if location:
            return location.latitude, location.longitude
        else:
            location = geolocator.geocode(f"{province_name}, Thailand", timeout=10)
            if location:
                return location.latitude, location.longitude
            else:
                return None, None

    except GeocoderTimedOut:
        return get_coordinates(venue_name, province_name)
    except Exception as e:
        print(f"Geocoding Error: {e}")
        return None, None
    
def get_province_thailand(lat, lon):
    if not lat or not lon:
        return None
    try:
        time.sleep(1)
        coordinates = f"{lat}, {lon}"
        location = geolocator.reverse(coordinates, language='th')
        
        if location:
            address = location.raw.get('address', {})
            province = address.get('province') or address.get('state') or address.get('city')
            
            if province:
                clean_province = province.replace("จังหวัด", "").strip()
                if "มหานคร" in clean_province:
                     return "กรุงเทพมหานคร"
                return clean_province
                
    except Exception as e:
        print(f"Reverse Geo Error: {e}")
        return None
    return None