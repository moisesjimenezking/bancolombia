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
import time
import logging
import os


logging.basicConfig(level=logging.DEBUG)

class ScriptBancolombia:
    driver = None
    NIT   = str(nit)
    CC    = str(cc)
    boxCC = str(boxCc)
    listTime = None
    wait = None


    @classmethod
    def initialize(cls, data):
        cls.listTime = data
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
        options = Options()
        options.add_argument("--headless")
        options.add_argument(f"--user-agent={user_agent}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.binary_location = '/usr/bin/firefox-esr'

        cls.driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)

        response = cls.login()
        time.sleep(1.5)
        cls.driver.quit()
        return response

    @classmethod
    def login(cls):
        cls.driver.get("https://sucursalvirtualpyme.bancolombia.com/#/login")
        cls.wait = WebDriverWait(cls.driver, 15)

        cls.loginNit()
        time.sleep(1.5)

        cls.loginCC()
        time.sleep(1.5)
        
        #* Presionar el boton de continuar
        buttonLogin = cls.wait.until(EC.presence_of_element_located((By.XPATH, '//button[@id="button-continue-login"]')))
        buttonLogin.click()
        time.sleep(1.5)

        cls.cashierKey()
        time.sleep(1.5)

        #* Aceder a la lista de movimientos
        buttonMovements = cls.wait.until(EC.presence_of_element_located((By.XPATH, '//a[contains(text(), "Consultas")]')))
        buttonMovements.click()
        buttonMovements = cls.wait.until(EC.presence_of_element_located((By.XPATH, '//a[@id="button-dashboard-movements"]')))
        buttonMovements.click()
        time.sleep(1.5)

        #* Obtener movimientos
        response = cls.movements()
        return response

    @classmethod
    def movements(cls):
        while True:
            end = False
            listMovements = list()
            strMovements = ""
            time.sleep(2)
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
    def consult(cls, data):
        if "start_date" not in data:
            data["start_date"] = datetime.now().strftime("%Y-%m-%d")

        start_date = datetime.strptime(data["start_date"], "%Y-%m-%d")
        end_date  = (start_date - timedelta(days=1))

        listTime = [start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")]

        result = ScriptBancolombia.initialize(listTime)

        rute = cls.buildPdf(result["movements"])
        response = {"text":result["text"], "file_url":rute["rute"]}
        return {
            "response":response,
            "status_http":200
        }
    
    @classmethod
    def buildPdf(cls, data):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)

        col_widths = [10, 30, 40, 100]

        pdf.cell(col_widths[0], 10, "Nª", border=1, align='C')
        pdf.cell(col_widths[1], 10, "Fecha", border=1, align='C')
        pdf.cell(col_widths[2], 10, "Monto", border=1, align='C')
        pdf.cell(col_widths[3], 10, "Descripción", border=1, ln=True, align='C')
        
        aux = 1
        for item in data:
            pdf.cell(col_widths[0], 10, f"#{aux}", border=1, align='C')
            pdf.cell(col_widths[1], 10, item['date'], border=1, align='C')
            pdf.cell(col_widths[2], 10, item['amount'], border=1, align='C')
            pdf.cell(col_widths[3], 10, item['description'], border=1, ln=True, align='C')

            aux += 1

        ruteLog = "config/logs/movements/"
        if not os.path.exists(ruteLog):
            os.makedirs(ruteLog)

        archive = "movimientos_{}.pdf".format(datetime.now().strftime("%Y-%m-%d"))
        # Guardar el PDF en un archivo
        pdf.output(ruteLog+archive)

        return {"rute":"{}pdf/{}".format(request.host_url, archive.replace(".pdf", ""))}