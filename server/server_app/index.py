from __init__ import app

@app.route("/")
def home():
    return "Hello world!!!"

if __name__ == '__main__':
    app.run()