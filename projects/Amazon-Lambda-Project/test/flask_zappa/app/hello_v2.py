from app import webapp
from flask import render_template, redirect, url_for, request, g
@webapp.route('/hello_word_v2')
def hello_world_v2():
    return redirect("http://54.226.181.175:5000", UserId = "shanxin")

