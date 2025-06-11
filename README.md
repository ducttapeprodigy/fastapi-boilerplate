# fastapi-boilerplate
Quick example of FastAPI service with simple authentication and RBAC and simulated CRUD operations.

# Setup Instructions

## Create venv
open a terminal in root of this repo and run:
linux: `python -m venv ./venv`
then 
`./venv/scripts/activate`
`python -m pip install -r requirements.txt`

## Run the service
from the activated venv in terminal:
`python main.py`
should result in output like: 
```
INFO:     Started server process [26616]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```