#!/bin/bash

# so, gunicorn binds port 8000 on localhost, changes directory to blog, launches 4 workers (4 pid's) which serve the flask application by getting an app object from views.py

#gunicorn -w 4 -b 127.0.0.1:8000 --chdir blog --log-level debug --reload views:app & 
#gunicorn -w 1 -b endovelicus.network:8000 --chdir blog --log-level debug --reload views:app & 
gunicorn -k gevent --worker-connections 1000 -b endovelicus.network:8000 --chdir blog --log-level debug --reload views:app & 
