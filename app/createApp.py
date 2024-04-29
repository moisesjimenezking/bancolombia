from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config["FLASK_DEBUG"] = False
CORS(app, supports_credentials=True)

telegramToken = os.getenv("TOKEN_TELEGRAM")
nit = os.getenv("NIT")
cc = os.getenv("CC")
boxCc = os.getenv("BOXCC")