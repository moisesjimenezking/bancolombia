from datetime import datetime, timedelta
from . import nit, cc, boxCc
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from weasyprint import HTML
from fpdf import FPDF
from flask import request
from createApp import app
import time
import logging
import os
import json
import threading



logging.basicConfig(level=logging.DEBUG)

class ScriptBancolombia:
    driver = None
    NIT   = str(nit)
    CC    = str(cc)
    boxCC = str(boxCc)
    listTime = None
    wait = None


    @classmethod
    def initialize(cls, listTimeInit, account):
        cls.listTime = listTimeInit
        cls.CC    = account["cc"] if "cc" in account else cls.CC
        cls.NIT   = account["nit"] if "nit" in account else cls.NIT
        cls.boxCC = account["boxCc"] if "boxCc" in account else cls.boxCC

        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
        options = Options()
        options.add_argument("--headless")
        options.add_argument(f"--user-agent={user_agent}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.binary_location = "/usr/bin/firefox-esr"

        cls.driver = webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()), options=options
        )
        
        response = cls.login()

        cls.driver.quit()
        return response

    @classmethod
    def login(cls):
        cls.driver.get("https://sucursalvirtualpyme.bancolombia.com/#/login")
        cls.wait = WebDriverWait(cls.driver, 15)

        cls.loginNit()
        time.sleep(1)

        cls.loginCC()
        time.sleep(1)
        
        #* Presionar el boton de continuar
        buttonLogin = cls.wait.until(EC.presence_of_element_located((By.XPATH, '//button[@id="button-continue-login"]')))
        buttonLogin.click()
        time.sleep(1)

        cls.cashierKey()
        time.sleep(1)

        #* Aceder a la lista de movimientos
        buttonMovements = cls.wait.until(EC.presence_of_element_located((By.XPATH, '//a[contains(text(), "Consultas")]')))
        buttonMovements.click()
        buttonMovements = cls.wait.until(EC.presence_of_element_located((By.XPATH, '//a[@id="button-dashboard-movements"]')))
        buttonMovements.click()
        time.sleep(1)

        #* Obtener movimientos
        response = cls.movements()
        return response

    @classmethod
    def movements(cls):
        while True:
            end = False
            listMovements = list()
            strMovements = ""
            time.sleep(5)
            table_element = cls.wait.until(EC.presence_of_element_located((By.ID, 'tblMyMovements')))
            rows = table_element.find_elements(By.TAG_NAME, 'tr')

            for row in rows:
                columns = row.find_elements(By.TAG_NAME, 'td')
                columns = [column.text for column in columns]
                if len(columns) >= 1 and len(columns[0]) > 1:
                    date = datetime.strptime(columns[0], "%Y-%m-%d")
                    date = date.strftime("%Y-%m-%d")
                    if date in cls.listTime:
                        listMovements.append({
                            "date":columns[0],
                            "amount":columns[1],
                            "description":columns[2],
                        })
                        strMovements = strMovements + "{} | {} | {} \n".format(columns[0], columns[1], columns[2])
                    else:
                        end = True
                        break
            
            if end:
                break

            buttonNext = cls.wait.until(EC.presence_of_element_located((By.ID, 'u-moreMovements-movements')))
            buttonNext.click()


        return {"movements":listMovements, "text":strMovements}

    @classmethod
    def cashierKey(cls):
        #? Pagina siguiente Clave de cajero
        inputPcc = cls.wait.until(EC.presence_of_element_located((By.XPATH, '//input[@id="input-password-key"]')))
        inputPcc.send_keys(cls.boxCC)

        buttonLogin = cls.wait.until(EC.presence_of_element_located((By.XPATH, '//button[@id="button-enter-login"]')))
        buttonLogin.click()


    @classmethod
    def loginCC(cls):
        #*Selecionar tipo de identificacion Cedula de ciudadania
        buttonList = cls.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="mat-form-field-infix ng-tns-c161-4"]')))
        buttonList.click()
        buttonSelectCc = cls.wait.until(EC.presence_of_element_located((By.XPATH, '//span[@class="mat-option-text"]//small[@id="item-documentType-login-CC"]')))
        buttonSelectCc.click()

        #* Ingresar CC
        inputCC = cls.wait.until(EC.presence_of_element_located((By.XPATH, '//input[@id="input-documentId-repres"]')))
        inputCC.send_keys(cls.CC)
        time.sleep(3)

    @classmethod
    def loginNit(cls):
        #*Selecionar tipo de identificacion NIT
        buttonList = cls.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="mat-form-field-wrapper ng-tns-c161-1"]')))
        buttonList.click()
        buttonSelectNit = cls.wait.until(EC.presence_of_element_located((By.XPATH, '//span[@class="mat-option-text"]//small[@id="item-documentType-login-NT"]')))
        buttonSelectNit.click()
        
        #* Ingresar NIT
        inputNIT = cls.wait.until(EC.presence_of_element_located((By.XPATH, '//input[@id="input-documentId-login"]')))
        inputNIT.send_keys(cls.NIT)


class BanKColom:
    @classmethod
    def consultV2(cls, data):
        start_date = data["start_date"] if "start_date" in data else datetime.now().strftime("%Y-%m-%d")
        data.pop("start_date", None)

        accountData = data
        nit = data["nit"] if "nit" in data else "default"

        cls.createDir()

        try:
            ruteCache = "config/logs/movements_cache/cache_{}_{}.txt".format(start_date, nit)
            with open(ruteCache, 'r') as archivo:
                content = archivo.read()
        except:
            files = [file for file in os.listdir("config/logs/movements_cache/") if file.endswith(f"_{nit}.txt")]
            if len(files) > 0:
                newest_file = files[0]
                with open("config/logs/movements_cache/" + newest_file, 'r') as archivo:
                    content = archivo.read()
            else:
                content = ""

        response = eval(content) if len(content) > 1 else {"file_url":None}
        host = request.host_url

        startDate = datetime.strptime(start_date, "%Y-%m-%d")
        end_date  = (startDate - timedelta(days=1)).strftime("%Y-%m-%d")
        listTime = [start_date, end_date]

        host = request.host_url
        
        newCache = True
        ruteblock = "config/logs/movements_block/block.txt"
        if os.path.exists(ruteblock):
            createTime = os.path.getctime(ruteblock)
            currentTime = time.time()
            if currentTime - createTime <= 300:
                newCache = False
            else:
                os.remove(ruteblock)

        if newCache:
            with open(ruteblock, 'w') as archivo:
                archivo.write("block")
        
            cls.removeGeko()
            cls.daemonInit(listTime, accountData, nit, host)

        if response["file_url"] is None:
            aux = 0
            while True:
                files = [file for file in os.listdir("config/logs/movements/") if file.endswith(f"{start_date}_{nit}.pdf")]
                filesAux = [file for file in os.listdir("config/logs/movements/") if file.endswith(f".pdf") and start_date in file]
                newest_file = None
                if len(files) > 0:
                    newest_file = host+"pdf/"+files[0]
                else:
                    if len(filesAux) > 0:
                        newest_file = host+"pdf/"+filesAux[0]

                response["file_url"] = newest_file
                aux += 1
                time.sleep(1)

                if newest_file is not None:
                    break

                if aux == 90:
                    raise Exception("timeout", 404)
                
        return {
            "response":response,
            "status_http":200
        }
    
    @classmethod
    def createDir(cls):
        ruteDirectori = "config/logs/movements_cache/"
        if not os.path.exists(ruteDirectori):
            os.makedirs(ruteDirectori)

        ruteLog = "config/logs/movements/"
        if not os.path.exists(ruteLog):
            os.makedirs(ruteLog)

        ruteBlock = "config/logs/movements_block/"
        if not os.path.exists(ruteBlock):
            os.makedirs(ruteBlock)

    @classmethod
    def daemonInit(cls, listTime, accountData, nit, host):
        background_thread = threading.Thread(target=cls.daemon, args=(listTime, accountData, nit, host))
        background_thread.daemon = True
        background_thread.start()
        
        return True
    
    @classmethod
    def daemon(cls, listTime, accountData, nit, host):
        with app.app_context():
            try:
                result = ScriptBancolombia.initialize(listTime, accountData)
            except Exception as e:
                ruteblock = "config/logs/movements_block/block.txt"
                if os.path.exists(ruteblock):
                    os.remove(ruteblock)

                logging.debug(str(e))
                raise Exception("Error Script", 404)
            logging.debug(str("e22"))
            movements = result["movements"]

            #? BLOCK PDF 
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=10)

            col_widths = [10, 30, 40, 100]

            pdf.cell(col_widths[0], 10, "Nª", border=1, align='C')
            pdf.cell(col_widths[1], 10, "Fecha", border=1, align='C')
            pdf.cell(col_widths[2], 10, "Monto", border=1, align='C')
            pdf.cell(col_widths[3], 10, "Descripción", border=1, ln=True, align='C')
        
            aux = 1
            for item in movements:
                pdf.cell(col_widths[0], 10, f"#{aux}", border=1, align='C')
                pdf.cell(col_widths[1], 10, item['date'], border=1, align='C')
                pdf.cell(col_widths[2], 10, item['amount'], border=1, align='C')
                pdf.cell(col_widths[3], 10, item['description'], border=1, ln=True, align='C')

                aux += 1

            archive = "movimientos_{}_{}.pdf".format(datetime.now().strftime("%Y-%m-%d"), nit)
            pdf.output("config/logs/movements/"+archive)

            rute = "{}pdf/{}".format(host, archive)

            ruteCache = "config/logs/movements_cache/cache_{}_{}.txt".format(datetime.now().strftime("%Y-%m-%d"), nit)
            response = {"file_url":rute}

            with open(ruteCache, 'w') as archivo:
                archivo.write(json.dumps(response))

            ruteblock = "config/logs/movements_block/block.txt"
            if os.path.exists(ruteblock):
                os.remove(ruteblock)

    @classmethod
    def removeGeko(cls):
        try:
            file_path = '/root/.wdm/drivers/geckodriver/linux64/v0.34.0/geckodriver'
            if os.path.exists(file_path):
                os.remove(file_path)
                logging.debug(f"El archivo {file_path} ha sido eliminado.")
            else:
                logging.debug(f"El archivo {file_path} no existe.")
        except Exception:
            pass