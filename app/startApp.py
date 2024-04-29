from createApp import app
from flask import jsonify, make_response

from modules.bancolombia import controller


@app.errorhandler(405)
def handle_not_allowed_error(error):
    response = {
        'response':{'message': "Método no accesible."},
        'status_http': 405
    }
        
    response = make_response(jsonify(response["response"]), response["status_http"])
    response.headers['Content-Type'] = 'application/json'
    response.headers['Accept-Encoding'] = 'gzip'
    return response

@app.errorhandler(404)
def handle_not_found_error(error):
    response = {
        "response": {"message": "Pagina no encontrada."}, 
        "status_http": 404
    }

    response = make_response(jsonify(response["response"]), response["status_http"])
    response.headers['Content-Type'] = 'application/json'
    response.headers['Accept-Encoding'] = 'gzip'
    return response

# ? Método para verificar la actividad de la app
@app.route("/api/v1/healthcheck", methods=["GET"])
def healthcheck():
    response = {
        'response':{'message': "OK"},
        'status_http': 200
    }
        
    response = make_response(jsonify(response["response"]), response["status_http"])
    response.headers['Content-Type'] = 'application/json'
    response.headers['Accept-Encoding'] = 'gzip'
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)