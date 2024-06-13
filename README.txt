EcoSmartBin
Project Description
EcoSmartBin is a waste management project designed to optimize the collection of waste bins in a city. The system clusters bins based on their locations and calculates the most efficient route for each cluster to assist collection teams. The project uses Fetch AI agents to handle data processing and route optimization.

Instructions to Run
Prerequisites
Ensure you have the following installed:

Python 3.8+
All required packages listed in requirements.txt
Setup
Clone the repository:

bash
Copy code
git clone <repository_url>
cd EcoSmartBin
Install the required packages:

bash
Copy code
pip install -r requirements.txt
Set up environment variables:
Create a .env file in the root directory and add your API keys:

env
Copy code
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
MAPBOX_ACCESS_TOKEN=your_mapbox_access_token
Generate Test Data
Before running the application, generate test data using the provided script:

bash
Copy code
python generate_test_data.py
This will create a test_data.csv file containing sample bin locations.

Running the Application
Start the Fetch AI Agent:

bash
Copy code
python agents.py
Ensure the agent is running and note the printed agent address.

Start the Flask Application:

bash
Copy code
python app.py
The Flask application will start on http://localhost:5004.

Use Case Example
Access the Flask Application:
Open a web browser and go to http://localhost:5004.

View Optimized Routes:
The application will query the Fetch AI agent with the test data, and you will see the optimized clusters and routes for bin collection.