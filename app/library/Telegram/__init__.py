from flask     import request
from createApp import telegramToken
import requests



#TODO: List Channels
listChannels = {
    "TEST_CHANNEL_BANCOLOMBIA"  : "-1002103514647", #* canal de test bancolombia
    "ALERT_CHANNEL_BANCOLOMBIA" : "-1001995855929", #* canal de alertas bancolombia
}


def sendMessage(message, channel=None):
    try:
        channel = listChannels[channel] if channel in listChannels else listChannels["TEST_CHANNEL_BANCOLOMBIA"]

        url = f'https://api.telegram.org/bot{telegramToken}/sendMessage'

        params = {
            'chat_id'    : channel,
            'parse_mode' : 'HTML',
            'text'       : f"{message} - bancolombia Temporal"
        }
        
        response = requests.post(url, params=params)
        response = response.json()

        if response["ok"] is False:
            raise Exception(response["description"] if "description" in response else "envio fallido")

    except Exception as e:
        response = {
            "response"    : {"message":"Envio Fallido "+str(e)},
            "status_http" : 400
        }

    return response