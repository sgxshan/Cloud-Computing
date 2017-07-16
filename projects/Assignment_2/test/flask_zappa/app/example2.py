
from flask import render_template, url_for
from app import webapp

import datetime
    
@webapp.route('/time_and_logo2')
def example2():
    time = datetime.datetime.now()  
    imgURL = url_for('static', filename='flask_logo.png')
    return render_template("example2.html",
                           time=time,
                           imgURL = imgURL)