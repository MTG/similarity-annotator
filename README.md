# Similarity Annotation Tool

A web based tool to annotate similarity of sounds regarding a target sound

## Installation

### Step 1: Python version
The project is written in python3 and will also works with python2, although we encourage the first.

### Step 2: Python Virtual Environments
To minimize the problems of dependencies and versions, we will take advantage of python's [virtualenv] (http://virtualenv.readthedocs.org/en/latest/index.html) tool to create isolated Python environments.

Follow [virtualenv](http://virtualenv.readthedocs.org/en/latest/virtualenv.html#installation)'s installation guide, create a virtual environment activate it in your shell.

### Step 3: Required packages
Having cloned this repository, use python's `pip` tool to install all the required packages for this similarity-annotation app. All the requirements specifications are maintained in `requirements.txt` file in the root directory.

    - pip install -r requirements.txt

### Step 4: Other packages
You need to install [node.js and npm] (https://docs.npmjs.com/getting-started/installing-node).
Then go you'll need to install npm in /similarity-annotator/static:

    - cd /similarity_annotator/static
    - npm install

### Step 5: Local configurations
Inside `similarity_annotator` directoy, rename `local_settings.py.dist` to `local_settings.py`

### Step 6: Database setup
On default, we are using a light-weight sqlite database but you are welcome to experiment with any database format that is compatibile with django. The database settings are configured in the `local_settings.py` file. Regardless if you change the database settings or not, you need to synchorinize your database with django models:

    - python manage.py syncdb
When prompted to create a superuser say 'No'. (You can create the superuser later in 'shell_plus')

    - python manage.py migrate

### Step 7: Running the server

To run the app simply run the following:

    python manage.py runserver

The we application will run on http://localhost:8000/


