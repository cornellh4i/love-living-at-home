# love-living-at-home
Repository for the Love Living at Home volunteer management system.

## Clone the repo!

If you have SSH setup with your Cornell GitHub account:
```
$ git clone git@github.coecis.cornell.edu:hack4impact-cornell/flask-demo.git 
```
Otherwise:
```
$ git clone https://github.coecis.cornell.edu/hack4impact-cornell/flask-demo.git
```

## Setup Virtual Environment 
```
$ cd path/to/repo
```
Windows:
```
$ python3 -m venv env
$ env\Scripts\activate.bat
```

Unix/MacOS:
```
$ python3 -m venv env
$ source env/bin/activate
```

Make sure your virtual environment is up and running before the next step!
```
$ pip3 install -r requirements.txt
```

## Run the app
```
$ export FLASK_ENV=development
$ flask run
```
