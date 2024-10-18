# Klimb Knowledge Test

Klimb Knowledge Test

## Steps to Configure This Project

### Previous Steps
1. Install Python 3.9 and pip.

### Steps
2. Create a virtual environment in the root of the project:
   ```bash
   python -m venv ./venv

<code>python -m venv ./venv</code>

3. Add important paths to $PYTHONPATH (advise: add it in ./venv/bin/activate)
<code>export HOME_PATH=</code>your root of project (example: C://user/project)
<code>export PYTHONPATH="$HOME_PATH/packages/python:$HOME_PATH/db/python:$HOME_PATH/shared/python:$HOME_PATH"</code>

4. install fastapi and alembic:
<code>pip install "fastapi[standard]"</code>
<code>pip install alembic</code>

5. Install dependencies
<code>pip install -t packages/python -r requirements.txt</code>

6. Set environment variables en a .env file

After cloning the repository and installing all needed packages, first configure Alembic. See Alembic Tutorial for instructions: 
a. Run alembic init alembic
b. Configure the env.py file in the alembic folder:
    1. Export the models and the URL of the DB.
c. Create the migration:
    1. Run alembic revision --autogenerate -m "first migration"
    2. Run alembic upgrade head

With these steps, you can configure the database.

If you don't have a database, only a file with data, put only the path of that file.
Once you have the project configured, run in the /src directory:
<code>uvicorn main:app --reload --log-level debug</code>

and open the route in a web browser to navigate inside the project.

This is the Swagger UI documentation of the API:
your_url:port/docs#/default

