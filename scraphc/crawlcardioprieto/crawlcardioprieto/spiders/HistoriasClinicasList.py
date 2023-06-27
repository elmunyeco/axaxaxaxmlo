import scrapy
import time
from .CookieHandler import CookieHandler

class HistoriasClinicas(scrapy.Spider):
    name = 'hhcc'
    start_urls = ["https://estudioadb.com/hc/index.php/hClinica/index"]

    def start_requests(self):
        # Obtener las cookies válidas
        cookies = self.get_valid_cookies()

        # Si las cookies son válidas, realizar la solicitud inicial
        if cookies is not None:
            yield scrapy.Request(url=self.start_urls[0], cookies=cookies, callback=self.parse_hhcc)

    def get_valid_cookies(self):
        max_attempts = 3  # Número máximo de intentos
        current_attempt = 1

        while current_attempt <= max_attempts:
            try:
                # Intentar cargar las cookies
                cookies = CookieHandler.load_cookies()
                # Verificar si las cookies son válidas
                if self.are_cookies_valid(cookies):
                    return cookies

                # Las cookies no son válidas, esperar antes de realizar un nuevo intento          
                time.sleep(5)  # Puedes ajustar el tiempo de espera aquí

                current_attempt += 1
            except Exception as e:
                # Ocurrió un error al cargar las cookies, esperar antes de realizar un nuevo intento
                time.sleep(5)  # Puedes ajustar el tiempo de espera aquí

                current_attempt += 1
                
        return None

    def are_cookies_valid(self, cookies):
        # Verificar si las cookies son válidas
        # Aquí puedes agregar tu lógica de validación de cookies
        # Por ejemplo, puedes realizar una solicitud de prueba al servidor para verificar su autenticidad
        return False

    def parse_hhcc(self, response):
        # Encuentra las filas de la tabla
        rows = response.xpath('//table[@id="dataTables-example"]/tbody/tr')

        for row in rows:
            # Extrae el valor del campo #1 (primer td)
            value = row.xpath('.//td[1]/text()').get()

            # Imprime el valor en la consola
            print(value)
