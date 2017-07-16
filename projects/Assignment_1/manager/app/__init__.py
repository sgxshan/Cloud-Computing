
from flask import Flask

webapp = Flask(__name__)

from app import manage

from app import account
from app import delete
from app import main

