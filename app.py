import json
from flask import Flask, jsonify, render_template
import pandas as pd
from uagents.query import query
from uagents import Model
from optimization import constrained_kmeans,get_routes_for_clusters,generate_plot

# Define the path to the CSV file
csv_file_path = './test_data.csv'

# Read the CSV file
with open(csv_file_path, 'r') as file:
    csv_data = file.read()

# Address of the agent handling the request
address = 'agent1q0vqy8fqk04uazxjrfp0q575h867ua6q953kvl9nj898wazea7r5uuqt06y'

app = Flask(__name__)

# Define the input data model
class InputData(Model):
    content: str

# Define the result data model
class ResultData(Model):
    cluster_js: str
    route_js: str

@app.route('/', methods=['GET'])
async def index():
    try:
        ## Query Function is not working without any reason.
        ## beacuse of that the calling agent code commented 
        ## and handeled by optimization file.
        ## USE ONLY one OF THE SECTION 1 OR 2.

# SECTION 1
        # Send the CSV data in the query
        #  data_bounds = {
        #     'lat_min': data[:, 0].min(),
        #     'lat_max': data[:, 0].max(),
        #     'lon_min': data[:, 1].min(),
        #     'lon_max': data[:, 1].max()
        # }
        # response =  await query(destination=address, message=InputData(content="csv_data"), timeout=15.0)
        
        # if response is None:
        #     return jsonify({'error': 'No response from agent'}), 500
        
        # responseData = json.loads(response.decode_payload())
        # plot_html = generate_plot(responseData.clusters_js, responseData.routes_js, data_bounds)
        
        # return render_template('index.html', plot_html=plot_html)

#SECTION 2
        data = pd.read_csv('test_data.csv').to_numpy()
        max_points_per_cluster = 20
        max_distance = 0.002  # Adjust as needed (approx. 200 meters)

        clusters = constrained_kmeans(data, max_points_per_cluster, max_distance)
        routes = get_routes_for_clusters(clusters)
        
        data_bounds = {
            'lat_min': data[:, 0].min(),
            'lat_max': data[:, 0].max(),
            'lon_min': data[:, 1].min(),
            'lon_max': data[:, 1].max()
        }
        
        plot_html = generate_plot(clusters, routes, data_bounds)
        
        return render_template('index.html', plot_html=plot_html)


    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5004)
