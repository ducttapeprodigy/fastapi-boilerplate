# fastapi-boilerplate
Quick example of FastAPI service with simple authentication and RBAC and simulated CRUD operations.

# Setup Instructions
## Create venv
Open a terminal in root of this repo and run:  
`python -m venv ./venv`  
Modify the `./venv/pyvenv.cfg` file to have:  
`include-system-site-packages = true`  
save the .cfg then run:  
`./venv/scripts/activate`  
and install all the python modules by running:  
`python -m pip install -r requirements.txt`

## Run the service
from the activated venv in terminal:  
`python main.py`  
should result in output like:  
```
INFO:     Started server process [26616]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

## FastAPI Auto-Documentation access:
Once the service is running, it should be possible to access by going to:  
http://localhost:8080/docs/