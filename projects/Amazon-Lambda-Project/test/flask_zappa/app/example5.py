from flask import render_template, session
from app import webapp

import datetime

webapp.secret_key = '\x80\xa9s*\x12\xc7x\xa9d\x1f(\x03\xbeHJ:\x9f\xf0!\xb1a\xaa\x0f\xee'

@webapp.route('/count',methods=['GET','POST'])
def count():
    numtimes = 0
    if 'numtimes' in session:
        numtimes = session['numtimes']
    session['numtimes'] = numtimes + 1
    session.permanent = True

    return render_template("example5.html",numtimes=numtimes)

