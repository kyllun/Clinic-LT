from flask import render_template, url_for
from server_app import app

@app.route("/")
def home_page():
    return render_template("home_page.html")

if __name__ == '__main__':
    app.run(debug=True)