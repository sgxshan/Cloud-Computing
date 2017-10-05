
from flask import redirect
from app import webapp

import datetime


@webapp.route('/')
def main():
    return redirect("http://54.196.15.77:5000")
    #return redirect("http://www.google.com")

