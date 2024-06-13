import numpy as np
import pandas as pd
import plotly.graph_objects as go
from flask import Flask, render_template
from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist
from dotenv import load_dotenv
import googlemaps
import os

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()
MAPBOX_ACCESS_TOKEN = os.getenv('MAPBOX_ACCESS_TOKEN')
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

def constrained_kmeans(data, max_points_per_cluster=20, max_distance=None):
    def fit_kmeans(data, n_clusters):
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        kmeans.fit(data)
        return kmeans

    def split_large_clusters(points, max_points_per_cluster):
        n_sub_clusters = (len(points) // max_points_per_cluster) + 1
        sub_kmeans = fit_kmeans(np.array(points), n_sub_clusters)
        sub_clusters = []
        for sub_label in np.unique(sub_kmeans.labels_):
            sub_cluster_points = np.array(points)[sub_kmeans.labels_ == sub_label]
            sub_clusters.append(sub_cluster_points)
        return sub_clusters

    def filter_clusters(data, labels, max_points_per_cluster, max_distance):
        clusters = {}
        for i, label in enumerate(labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(data[i])
        
        filtered_clusters = []
        for points in clusters.values():
            if len(points) > max_points_per_cluster:
                sub_clusters = split_large_clusters(points, max_points_per_cluster)
                filtered_clusters.extend(sub_clusters)
            else:
                filtered_clusters.append(np.array(points))
        
        if max_distance is not None:
            final_clusters = []
            for cluster in filtered_clusters:
                centroid = np.mean(cluster, axis=0)
                distances = cdist(cluster, [centroid])
                within_distance = cluster[distances.flatten() <= max_distance]
                final_clusters.append(within_distance)
            return final_clusters
        return filtered_clusters

    n_initial_clusters = max(1, len(data) // max_points_per_cluster)
    initial_kmeans = fit_kmeans(data, n_initial_clusters)
    filtered_clusters = filter_clusters(data, initial_kmeans.labels_, max_points_per_cluster, max_distance)
    return filtered_clusters

def calculate_initial_zoom(lat_range, lon_range):
    max_range = max(lat_range, lon_range)
    zoom = np.log2(360 / max_range) - 1
    return zoom

def get_routes_for_clusters(clusters):
    routes_info = []
    for cluster in clusters:
        if len(cluster) > 1:
            waypoints = [{"lat": lat, "lng": lon} for lat, lon in cluster]
            start = waypoints[0]
            end = waypoints[-1]
            waypoints = waypoints[1:-1]

            response = gmaps.directions(
                origin=start,
                destination=end,
                waypoints=waypoints,
                mode="driving"
            )
            routes_info.append(response)
    return routes_info

def generate_plot(clusters, routes, data_bounds):
    fig = go.Figure()

    # Define a list of colors
    colors = [
        'red', 'blue', 'green', 'purple', 'orange', 'yellow', 
        'brown', 'pink', 'gray', 'cyan', 'magenta', 'lime', 
        'maroon', 'navy', 'olive', 'teal'
    ]

    for i, cluster in enumerate(clusters):
        cluster = np.array(cluster)
        fig.add_trace(go.Scattermapbox(
            lon=cluster[:, 1], lat=cluster[:, 0],
            mode='markers',
            marker=dict(size=10),
            name=f'Cluster {i+1}'
        ))

    for i, route in enumerate(routes):
        color = colors[i % len(colors)]  # Cycle through the colors
        for leg in route[0]['legs']:
            steps = leg['steps']
            route_lat = []
            route_lon = []
            for step in steps:
                start_location = step['start_location']
                end_location = step['end_location']
                route_lat.append(start_location['lat'])
                route_lon.append(start_location['lng'])
                route_lat.append(end_location['lat'])
                route_lon.append(end_location['lng'])
            
            fig.add_trace(go.Scattermapbox(
                lon=route_lon, lat=route_lat,
                mode='lines',
                line=dict(width=2, color=color),
                name=f'Route {i+1}'
            ))

    # Calculate the margin
    lat_margin = (data_bounds['lat_max'] - data_bounds['lat_min']) * 0.10
    lon_margin = (data_bounds['lon_max'] - data_bounds['lon_min']) * 0.10
    
    center_lat = (data_bounds['lat_min'] + data_bounds['lat_max']) / 2
    center_lon = (data_bounds['lon_min'] + data_bounds['lon_max']) / 2
    
    lat_range = data_bounds['lat_max'] - data_bounds['lat_min'] + 2 * lat_margin
    lon_range = data_bounds['lon_max'] - data_bounds['lon_min'] + 2 * lon_margin
    zoom = calculate_initial_zoom(lat_range, lon_range)
    
    fig.update_layout(
        title="Clustered GPS Data Points in City of London",
        mapbox=dict(
            accesstoken=MAPBOX_ACCESS_TOKEN,
            style="streets",
            center=dict(lat=center_lat, lon=center_lon),
            zoom=zoom,
        ),
        autosize=True,
        height=800,
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    return fig.to_html(full_html=False)

def generate_plot(clusters, routes, data_bounds):
    fig = go.Figure()

    # Define a list of colors
    colors = [
        'red', 'blue', 'green', 'purple', 'orange', 'yellow', 
        'brown', 'pink', 'gray', 'cyan', 'magenta', 'lime', 
        'maroon', 'navy', 'olive', 'teal'
    ]

    for i, cluster in enumerate(clusters):
        cluster = np.array(cluster)
        fig.add_trace(go.Scattermapbox(
            lon=cluster[:, 1], lat=cluster[:, 0],
            mode='markers',
            marker=dict(size=10),
            name=f'Cluster {i+1}'
        ))

    for i, route in enumerate(routes):
        color = colors[i % len(colors)]  # Cycle through the colors
        for leg in route[0]['legs']:
            steps = leg['steps']
            route_lat = []
            route_lon = []
            for step in steps:
                start_location = step['start_location']
                end_location = step['end_location']
                route_lat.append(start_location['lat'])
                route_lon.append(start_location['lng'])
                route_lat.append(end_location['lat'])
                route_lon.append(end_location['lng'])
            
            fig.add_trace(go.Scattermapbox(
                lon=route_lon, lat=route_lat,
                mode='lines',
                line=dict(width=2, color=color),
                name=f'Route {i+1}'
            ))

    # Calculate the margin
    lat_margin = (data_bounds['lat_max'] - data_bounds['lat_min']) * 0.10
    lon_margin = (data_bounds['lon_max'] - data_bounds['lon_min']) * 0.10
    
    center_lat = (data_bounds['lat_min'] + data_bounds['lat_max']) / 2
    center_lon = (data_bounds['lon_min'] + data_bounds['lon_max']) / 2
    
    lat_range = data_bounds['lat_max'] - data_bounds['lat_min'] + 2 * lat_margin
    lon_range = data_bounds['lon_max'] - data_bounds['lon_min'] + 2 * lon_margin
    zoom = calculate_initial_zoom(lat_range, lon_range)
    
    fig.update_layout(
        title="Clustered GPS Data Points in City of London",
        mapbox=dict(
            accesstoken=MAPBOX_ACCESS_TOKEN,
            style="streets",
            center=dict(lat=center_lat, lon=center_lon),
            zoom=zoom,
        ),
        autosize=True,
        height=800,
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    return fig.to_html(full_html=False)
