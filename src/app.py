from website import create_app
from flask_cors import CORS, cross_origin

app = create_app()
CORS(app)
cors = CORS(app, resources = {
    r"/*" : {
        "origins": "*"
    }
})

@app.route("/cors", methods=["GET"])
def cors():
    print("COrsed")
    return "corsed"


if __name__ == '__main__':
    app.run(debug=True)
