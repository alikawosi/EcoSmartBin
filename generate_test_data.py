import numpy as np
import pandas as pd

# Function to generate random GPS coordinates within the City of London
def generate_gps_coordinates(num_points):
    np.random.seed(42)  # For reproducibility
    lat_center = 51.515
    lon_center = -0.09
    lat_range = 0.01
    lon_range = 0.02

    latitudes = lat_center + lat_range * (np.random.rand(num_points) - 0.5)
    longitudes = lon_center + lon_range * (np.random.rand(num_points) - 0.5)

    return latitudes, longitudes

# Generate coordinates
num_points = 100
latitudes, longitudes = generate_gps_coordinates(num_points)

# Create a DataFrame
df = pd.DataFrame({
    'latitude': latitudes,
    'longitude': longitudes
})

# Save to CSV
df.to_csv('test_data.csv', index=False)

print(f"test_data.csv generated with {num_points} GPS coordinates.")
