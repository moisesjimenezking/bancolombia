
import os 
import datetime
from library.Telegram import sendMessage
from createApp import app, nit, cc, boxCc

#? Formato standard para los .txt de los logs
formatTextLogs = """
##############################\n\n
Fecha   : {}\n
Mensaje : {}\n
Error   : {}\n
Estatus : {}\n
method  : {}\n
rute    : {}\n    
origin  : {}\n
query   : {}\n
##############################\n\n
"""

#? Constructor y manejador de errores y logs
def handle_error(data):
    try:   
        ruteLog = "config/logs/"+data["path"]
        if not os.path.exists(ruteLog):
            os.makedirs(ruteLog)

        currentDate = datetime.datetime.now()

        file = open(ruteLog+data["doc"], "a")
        file.write(
            formatTextLogs.format(
                str(currentDate.strftime("%Y-%m-%d %H:%M:%S")), 
                data["message"], 
                data["error"], 
                data["status_http"],
                data["method"],
                data["rute"],
                data["origin"],
                data["query"]
            )
        )
        file.close()
        
        messageError = "Message:{}{}Error:{}{}Metodo:{}{}Ruta:{}{}Origen:{}{}Query:{}{}".format(
            data["message"],"\n\n",
            data["error"],  "\n",
            data["method"], "\n",
            data["rute"],   "\n",
            data["origin"], "\n",
            data["query"],  "\n",
        )

        sendMessage(messageError, "ALERT_CHANNEL_BANCOLOMBIA")

        return {
            'response':{
                "error":{
                    'internalError':data["error"], 
                    'message':data["message"]
                },
            },
            'status_http':data["status_http"]
        }
    except Exception as e:
        return {
            'response':{
                "error":{
                    'internalError':str(e), 
                    'message':data["message"]
                },
            },
            'status_http':data["status_http"]
        }