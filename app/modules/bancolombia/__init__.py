from flask import request
from .. import handle_error, app, nit, cc, boxCc


def handle_error_bancolombia(data):
    #* Se estandariza funcion que maneja los errores
    dataError = {
        "path": "bancolombia",
        "method": request.method,
        "rute": request.url,
        "origin": request.remote_addr,
        "doc": "/bancolombia.txt",
        "query": data["query"],
        "message": data["message"],
        "error": data["error"],
        "status_http": data["status_http"]
    }
        
    return handle_error(dataError)


def getRequestData(method = None):
    #* Default response
    response = {
        "data"        : None,
        "error"       : False,
        "status_http" : 200,
    }
    
    try:
        response["data"] = request.args or request.values or request.form or request.json
        response["data"] = response["data"].copy()
    except Exception:
        response["data"] = dict()
    
    #* Se validan los parámetros enviados y el token
    if method is not None:
        pass
        # validation = ParamValidation.ValidationParam(response["data"], method)
        # if validation["status_http"] != 200:
        #     response["error"] = validation["response"]["message"]
        #     response["status_http"] = validation["status_http"]
    
    return response 
