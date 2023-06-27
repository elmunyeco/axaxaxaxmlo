import os
import pickle
from datetime import datetime
import scrapy
from scrapy import signals

class CookieHandler:
    @staticmethod
    def load_cookies():
        if os.path.exists("cookies.pkl"):
            with open("cookies.pkl", "rb") as f:
                cookies = pickle.load(f)
            return cookies
        else:
            return None

    @staticmethod
    def save_cookies(cookies):
        with open("cookies.pkl", "wb") as f:
            pickle.dump(cookies, f)

    @staticmethod
    def are_cookies_valid(cookies):
        if cookies is None:
            return False

        # Verificar si las cookies están en el formato esperado
        if not isinstance(cookies, dict):
            return False

        # Comprobar si las cookies tienen una fecha de expiración futura
        for cookie_name, cookie_value in cookies.items():
            if "expires" in cookie_value:
                expires_str = cookie_value["expires"]
                expires_datetime = datetime.strptime(expires_str, "%a, %d-%b-%Y %H:%M:%S %Z")
                if expires_datetime < datetime.now():
                    return False

        return True


class LoginSpider(scrapy.Spider):
    name = 'login'
    login_url = "https://estudioadb.com/hc/index.php/login/validarUsuario"

    def start_requests(self):
        yield scrapy.FormRequest(url=self.login_url, formdata={'usuario': 'omar', 'pass': 'Corbis5'},
                                 callback=self.after_login)

    def after_login(self, response):
        if response.css('li.dropdown a[href*="/login/logout"]'):
            cookies = response.headers.getlist('Set-Cookie')
            CookieHandler.save_cookies(cookies)
            # Emitir una señal para indicar que se han guardado las cookies válidas
            self.crawler.signals.send_catch_log(signal=signals.cookie_saved, spider=self, cookies=cookies)


class HistoriasClinicas(scrapy.Spider):
    name = 'hhcc'
    start_urls = ["https://estudioadb.com/hc/index.php/hClinica/index"]

    def __init__(self, *args, **kwargs):
        super(HistoriasClinicas, self).__init__(*args, **kwargs)
        # Suscribirse a la señal cuando se guardan las cookies válidas
        self.crawler.signals.connect(self.cookies_saved, signal=signals.cookie_saved)

    def start_requests(self):
        cookies = CookieHandler.load_cookies()
        if cookies is not None and self.are_cookies_valid(cookies):
            yield scrapy.Request(url=self.start_urls[0], cookies=cookies, callback=self.parse_hhcc)
        else:
            login_spider = LoginSpider()
            yield from login_spider.start_requests()

    def cookies_saved(self, spider, cookies):
        # Se ejecuta cuando se emite la señal de cookies guardadas
        # Verificar si las cookies son válidas
        if self.are_cookies_valid(cookies):
            # Realizar la solicitud inicial ahora que se tienen las cookies válidas
            yield scrapy.Request(url=self.start_urls[0], cookies=cookies, callback=self.parse_hhcc)

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
