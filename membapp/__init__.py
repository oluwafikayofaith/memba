from flask  import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
#we want to make the object base config available
from membapp import config

app = Flask(__name__,instance_relative_config=True)

#instantiate object of csrf,this will protect all your post routes against csrf and you must pass the token
csrf = CSRFProtect(app)

#to load the config
app.config.from_pyfile('config.py',silent=False)
#load config ffrom object base config that is within your package
app.config.from_object(config.LiveConfig)

db=SQLAlchemy(app)
migrate=Migrate(app,db)

#to load the routes and form
from membapp import adminroutes,userroutes