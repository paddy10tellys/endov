import os # to interface with underlying operating system
from blog import app  # import the app variable from the blog package

#app.secret_key = os.urandom(24)
#app.run(debug=True, host = os.getenv('IP','0.0.0.0'), port=int(os.getenv('PORT',8080)))  


os.system("sh ./rungun.sh")    # call shell script from python code. This is for deployment phase

# the shell file rungun.sh launches gunicorn binds port 8000 on localhost, changes directory to blog, launches 4 workers (4 pid's) which serve the flask 
# application by getting an app object from views.py In Nicole White's tutorial this is     app.run(debug="True")
# but this launches the (toy) built-in web server that comes with flask & uses port 5000 on localhost - use gunicorn for deployment