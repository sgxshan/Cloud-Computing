
from flask import Flask

webapp = Flask(__name__)

from app import main
from app import Image
from app import user
from app import evaluate
#from app import test

