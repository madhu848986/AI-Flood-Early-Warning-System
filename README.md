\# AI-Driven Multimodal Flood Early-Warning and Dynamic Safe-Zone Recommendation System



\## Project Overview



This project is an AI-driven flood early-warning and decision-support system developed for the Koshi Basin, Nepal.



It combines rainfall data, satellite-derived flood information, geographical datasets, and road-network information to support flood-risk assessment and identify potentially safer locations and routes.



The system provides a web-based interface for viewing flood-risk information, forecasts, alerts, nearby shelters, and route recommendations.



\## Key Features



\- User registration and login

\- Flood risk visualization on an interactive map

\- Flood forecast and alert dashboard

\- Safest-place recommendations

\- Safest-route recommendations using a road network

\- Shelter finder

\- Automatic in-app flood-risk alerts for users with saved locations



\## Technology Stack



\*\*Frontend\*\*

\- React

\- Vite

\- Leaflet

\- React Leaflet



\*\*Backend\*\*

\- Python 3.12

\- FastAPI

\- Pandas

\- NumPy

\- NetworkX

\- SciPy

\- GeoPy

\- UTM



\*\*Data Sources and Geospatial Data\*\*

\- GPM IMERG rainfall data

\- Satellite-derived flood information

\- SRTM elevation data

\- OpenStreetMap road-network data



\## Project Structure



```text

Flood-Early-Warning/

├── backend/

├── frontend/

├── datasets/

│   └── processed/

├── notebooks/

├── requirements.txt

├── .gitignore

└── README.md

```



\## Requirements



\- Python 3.12

\- Node.js and npm

\- Git

\- Git LFS



\## Backend Setup



Open a terminal in the project root.



Create and activate a virtual environment:



```cmd

python -m venv .venv

.venv\\Scripts\\activate

```



Install the Python dependencies:



```cmd

pip install -r requirements.txt

```



Start the backend:



```cmd

python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

```



Backend API:



http://127.0.0.1:8000



API documentation:



http://127.0.0.1:8000/docs



\## Frontend Setup



Open another terminal:



```cmd

cd frontend

npm install

npm run dev

```



Open the frontend using the local URL displayed in the terminal, usually:



http://localhost:5173



\## Important Dataset Files



The following processed files are required by the application:



\- `koshi\_all\_grid\_flood\_predictions.csv`

\- `koshi\_shelter\_recommendations.csv`

\- `koshi\_top\_risk\_locations\_named.csv`

\- `safest\_place\_location\_cache.json`

\- `koshi\_bilinear\_flood\_risk\_road\_graph.graphml`



The road-network GraphML file is stored using Git LFS.



After cloning the repository, install Git LFS and run:



```cmd

git lfs pull

```



\## Important Notes



\- Raw satellite and large source datasets are not included in the Git repository.

\- The application uses the included processed datasets for its current features.

\- Each local installation creates and maintains its own user database.

\- Flood predictions and route recommendations are experimental research outputs. They are not official flood warnings or guaranteed safe routes.

\- Always follow instructions from local disaster-management authorities and verify shelter and road conditions before travelling.



\## Project Status



Design completed; implementation and testing in progress.

