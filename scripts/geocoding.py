import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import folium
import time
from scripts.data_preprocessing import preprocess_data

def geocode_dataframe(df):
    geolocator = Nominatim(user_agent="property_geocoder")

    def geocode_property(row):
        try:
            location = geolocator.geocode(
                row['Dirección Mapa'] + ', ' + str(row['Código Postal']) + ' ' + row['Localidad'] + ', ' + row['Provincia'],
                timeout=15
            )
            if location:
                return location.latitude, location.longitude
            else:
                return None
        except GeocoderTimedOut:
            return None

    # Apply geocoding to get coordinates and drop rows with invalid locations
    df['Coordinates'] = df.apply(geocode_property, axis=1)
    df = df.dropna(subset=['Coordinates'])
    return df

def create_map(df):
    # Create a Folium map centered in Spain
    map_center = [40.4168, -3.7038]  # Coordinates for the center of Spain
    property_map = folium.Map(location=map_center, zoom_start=6)

    # Add markers for each property with identifiers as popups
    located_count = 0  # Counter for located properties
    for _, row in df.iterrows():
        folium.Marker(
            location=row['Coordinates'],
            popup=row['Identificador'],
        ).add_to(property_map)
        located_count += 1

    # Print the number of located properties
    print(f"Number of located properties: {located_count}")

    # Save the map as an HTML file
    property_map.save('property_map_with_direccion_mapa.html')

if __name__ == '__main__':
    start_time = time.time()

    # Load and preprocess your DataFrame
    df = pd.read_csv('mapa_actualizado_with_direccion_mapa.csv')
    df = preprocess_data(df)

    # Geocode addresses and create the map
    geocoded_df = geocode_dataframe(df)
    create_map(geocoded_df)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Execution time: {elapsed_time:.2f} seconds")
