from flask import render_template, request
from app import webapp


@webapp.route('/add')
def add_two_numbers():
    if request.args.get('n1').isdigit() == False or \
       request.args.get('n2').isdigit() == False:
        return "Error! All inputs most be of type int"
    
    n1 = int(request.args.get('n1'))
    n2 = int(request.args.get('n2'))
    return render_template("example4.html",n1=n1, n2=n2, result=n1+n2)

@webapp.route('/add_v2',methods=['GET'])
def add_two_numbers_v2_form():
    return render_template("example4_form.html")


@webapp.route('/add_v2_submit',methods=['POST'])
def add_two_numbers_v2():
    if request.form.get('n1').isdigit() == False or \
       request.form.get('n2').isdigit() == False:
        return "Error! All inputs most be of type int"
    
    n1 = int(request.form.get('n1'))
    n2 = int(request.form.get('n2'))
    return render_template("example4.html",n1=n1, n2=n2, result=n1+n2)

@webapp.route('/add_v3',methods=['GET'])
def add_two_numbers_v3_form():
    return render_template("example4_form_v2.html")


@webapp.route('/add_v3_submit',methods=['POST'])
def add_two_numbers_v3():
    
    n1 = request.form.get('n1')
    n2 = request.form.get('n2')
    
    if n1.isdigit() == False or \
       n2.isdigit() == False:
        error="Error! All inputs most be of type int"
        return render_template("example4_form_v2.html", error=error,n1=n1, n2=n2)
    
    n1 = int(request.form.get('n1'))
    n2 = int(request.form.get('n2'))
    return render_template("example4.html",n1=n1, n2=n2, result=n1+n2)
