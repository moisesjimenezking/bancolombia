from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from weasyprint import HTML
import os
import time

class bankColombia:
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
    options = Options()
    # options.add_argument("--headless")
    options.add_argument(f"--user-agent={user_agent}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)

    NIT   = "901615052"
    CC    = "76323909"
    boxCC = "2528"

    @classmethod
    def process(cls):
        try:
            '''
                GET Login BanColombia
            '''
            #* Ingresar a bancolombia
            cls.driver.get("https://sucursalvirtualpyme.bancolombia.com/#/login")
            wait = WebDriverWait(cls.driver, 15)

            #*Selecionar tipo de identificacion NIT
            buttonList = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="mat-form-field-wrapper ng-tns-c161-1"]')))
            buttonList.click()
            buttonSelectNit = wait.until(EC.presence_of_element_located((By.XPATH, '//span[@class="mat-option-text"]//small[@id="item-documentType-login-NT"]')))
            buttonSelectNit.click()

            #* Ingresar NIT
            inputNIT = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@id="input-documentId-login"]')))
            inputNIT.send_keys(cls.NIT)
            time.sleep(3)

            #*Selecionar tipo de identificacion Cedula de ciudadania
            buttonList = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="mat-form-field-infix ng-tns-c161-4"]')))
            buttonList.click()
            buttonSelectCc = wait.until(EC.presence_of_element_located((By.XPATH, '//span[@class="mat-option-text"]//small[@id="item-documentType-login-CC"]')))
            buttonSelectCc.click()

            #* Ingresar CC
            inputCC = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@id="input-documentId-repres"]')))
            inputCC.send_keys(cls.CC)
            time.sleep(3)
            
            #* Presionar el boton de continuar
            buttonLogin = wait.until(EC.presence_of_element_located((By.XPATH, '//button[@id="button-continue-login"]')))
            buttonLogin.click()

            #? Pagina siguiente Clave de cajero
            inputPcc = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@id="input-password-key"]')))
            inputPcc.send_keys(cls.boxCC)

            #button 
            buttonLogin = wait.until(EC.presence_of_element_located((By.XPATH, '//button[@id="button-enter-login"]')))
            buttonLogin.click()
            
            #? Pagina dentro del banco
            buttonMovements = wait.until(EC.presence_of_element_located((By.XPATH, '//a[contains(text(), "Consultas")]')))
            buttonMovements.click()

            buttonMovements = wait.until(EC.presence_of_element_located((By.XPATH, '//a[@id="button-dashboard-movements"]')))
            buttonMovements.click()

            #? Pagina dentro del banco seccion movimientos
            for x in range(1):
                time.sleep(3)
                # table = wait.until(EC.presence_of_element_located,((By.XPATH, '//div[@class="card-body sv-padding-10 bg-white sv-border-gray sv-borderradius-5 ng-star-inserted"]')))
                table_element = wait.until(EC.presence_of_element_located((By.ID, 'tblMyMovements')))
                rows = table_element.find_elements(By.TAG_NAME, 'tr')

                # Recorrer cada fila e imprimir el texto de cada una
                for row in rows:
                    columns = row.find_elements(By.TAG_NAME, 'td')
                    for column in columns:
                        print(column.text)

                # Obtener el contenido HTML de la tabla
                table_html = table_element.get_attribute('outerHTML')
                # tablePDF = table.get_attribute('outerHTML')
                with open('temp.html', 'w') as f:
                    f.write(table_html)

                # Convertir el archivo HTML a PDF con WeasyPrint
                HTML('temp.html').write_pdf('elemento_{}.pdf'.format(x))
                os.remove('temp.html')

                time.sleep(3)
                buttonNext = wait.until(EC.presence_of_element_located((By.ID, 'u-moreMovements-movements')))
                # buttonNext = wait.until(EC.presence_of_element_located,((By.XPATH, '//div[@class"row sv-margin-b30 ng-star-inserted"]//div[@class="col text-center"]//u[@id=""]')))
                buttonNext.click()

        except Exception as e:
            print(str(e))
            cls.driver.quit()

        time.sleep(15)
        print("END")
        cls.driver.quit()


def main():
    bankColombia.process()

main()