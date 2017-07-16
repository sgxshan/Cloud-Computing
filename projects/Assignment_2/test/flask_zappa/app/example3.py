from flask import render_template, url_for
from app import webapp

@webapp.route('/collatz_steps/<int:n>')
def count_collatz_steps(n):
    """ (int) -> str
    
    Create a web page with the number of steps it takes to reach 1, by applying 
    the two steps of the Collatz conjecture beginning from n.

    """

    steps = 0
    while n != 1:
        if n % 2 == 0:
            n = n // 2
        else:
            n = n * 3 + 1
        steps = steps + 1

    return render_template("example3.html",steps=steps)



@webapp.route('/collatz_steps_v2/<int:n>')
def count_collatz_steps_verbose(n):
    """ (int) -> str
    
    Create a web page with the number of steps it takes to reach 1, by applying 
    the two steps of the Collatz conjecture beginning from n.

    """
    original = n
    
    steps = []
    
    while n != 1:
        if n % 2 == 0:
            n = n // 2
        else:
            n = n * 3 + 1
        steps.append(n)

    return render_template("example3_v2.html",n=original,steps=steps)
