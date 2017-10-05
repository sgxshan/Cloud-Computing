
from flask import render_template, url_for
from app import webapp

import datetime


@webapp.route('/time_and_logo')
def example1():
    time = datetime.datetime.now()  
    
    response = """<!DOCTYPE html>
                  <html>
                      <img width='100px' src="{}" />
                      Current Date and Time: {}
                  </html>
                  """
    
    return response.format(url_for('static', filename='flask_logo.png'),time)


