from flask import jsonify, request, make_response
from modules.bancolombia.model import BanKColom
from . import handle_error_bancolombia, getRequestData, app


@app.route('/api/v1/consult', methods=['GET'])
@app.route('/consult', methods=['GET'])
def controllerCode():
    try:
        listRoutes = {
            "/consult" : [BanKColom.consult, None]
        }

        key = (
            request.path+"_"+request.method.lower()
            if request.path+"_"+request.method.lower() in listRoutes
            else request.path
        )

        key = key.replace("/api/v1", "")

        if key not in listRoutes:
            raise Exception("Método no accesible.", 405)

        data = getRequestData(listRoutes[key][1])
        if data["status_http"] != 200:
            raise Exception(data["error"], data["status_http"])
            
        method = listRoutes[key][0].__get__(None, BanKColom)
        
        response = method(data["data"])
        
    except Exception as e:
        dataError = {
            "message": e.args[0] if len(e.args) > 1 else "Se ha producido un error en la aplicación. Por favor, intenta nuevamente más tarde.",
            "error": str(e),
            "status_http": e.args[1] if len(e.args) > 1 else 400,
            "query": data["data"] if "data" in locals() else None
        }
        
        response = handle_error_bancolombia(dataError)
    
    response = make_response(jsonify(response["response"]), response["status_http"])
    response = headerResponse(response)
    return response

def headerResponse(response):
    response.headers['Content-Type']    = 'application/json'
    response.headers['Accept-Encoding'] = 'gzip'
    return response