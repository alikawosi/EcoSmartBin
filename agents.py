import os
import json
import pandas as pd
import googlemaps
from sklearn.cluster import KMeans
from dotenv import load_dotenv
from uagents import Agent, Context, Model, Bureau
from uagents.setup import fund_agent_if_low

# Load environment variables from .env file
load_dotenv()

# Retrieve API key from environment variables
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
MAPBOX_ACCESS_TOKEN = os.getenv('MAPBOX_ACCESS_TOKEN')

# Initialize Google Maps client
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

# Define a protocol for the agent to handle the process

class InputData(Model):
        content: str

class ResultData(Model):
        cluster_js: str
        route_js: str

# Define the agent
agent = Agent(name='agent', seed="agent recovery phrase",port=5004,endpoint=['http://localhost:5004/submit'])
fund_agent_if_low(agent.wallet.address())
print(agent.address)


DATA_FILE = 'data_store.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

def generate_js(clusters, routes):
    cluster_js = []
    route_js = []

    colors = [
        'red', 'blue', 'green', 'purple', 'orange', 'yellow', 
        'brown', 'pink', 'gray', 'cyan', 'magenta', 'lime', 
        'maroon', 'navy', 'olive', 'teal'
    ]

    for i, cluster in enumerate(clusters):
        cluster_js.append({
            'color': colors[i % len(colors)],
            'points': cluster.tolist()
        })

    for i, route in enumerate(routes):
        route_points = []
        for leg in route[0]['legs']:
            steps = leg['steps']
            for step in steps:
                start_location = step['start_location']
                end_location = step['end_location']
                route_points.append([start_location['lat'], start_location['lng']])
                route_points.append([end_location['lat'], end_location['lng']])
        route_js.append({
            'color': colors[i % len(colors)],
            'points': route_points,
            'estimated_time': route[0]['legs'][0]['duration']['text']
        })

    return cluster_js, route_js

@agent.on_query(model=InputData,replies=ResultData)
async def qurey_handler(ctx:Context,sender:str, msg:InputData):
    try:
        # Load the existing data
        data = load_data()
        # Append the new data
        new_data = json.loads(msg.content)
        data.extend(new_data)

        # Clusterring and Save the updated data
        save_data(data)
        df = pd.DataFrame(data, columns=['latitude', 'longitude'])
        coords = df[['latitude', 'longitude']].values
        kmeans = KMeans(n_clusters=3).fit(coords)
        df['cluster'] = kmeans.labels_

        clusters = [df[df['cluster'] == i][['latitude', 'longitude']].values for i in range(3)]

        routes = []
        for cluster in clusters:
            if len(cluster) > 1:  # Ensure there are at least two points to create a route
                waypoints = [{'lat': point[0], 'lng': point[1]} for point in cluster]
                route = gmaps.directions(waypoints[0], waypoints[-1], waypoints=waypoints[1:-1], optimize_waypoints=True)
                routes.append(route)

        cluster_js, route_js = await generate_js(clusters, routes)
        #Send the result back
        await ctx.send(sender,ResultData(cluster_js=json.dumps(cluster_js), route_js=json.dumps(route_js)))
        
    except Exception as e:
        error_message = f"Error! {str(e)}"
        await ctx.logger.info(error_message)


if __name__ == '__main__':
    agent.run()
