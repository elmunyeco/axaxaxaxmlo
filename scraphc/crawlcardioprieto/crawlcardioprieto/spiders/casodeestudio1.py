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
        if cookies is not None and self.are_cookies_valid



"""
Gracias por proporcionar el código modificado. He revisado el código y aquí están mis comentarios:

En CookieHandler.load_cookies(), se agregó la creación de una instancia del spider LoginSpider y se obtuvieron las solicitudes de inicio de sesión mediante login_requests. Sin embargo, en este punto, no es posible esperar a que se completen las solicitudes del spider LoginSpider dentro de la función load_cookies(). La función load_cookies() se ejecuta de forma asíncrona y no se puede detener para esperar el resultado de otra función. Por lo tanto, no funcionará como se espera.

En CookieHandler.load_cookies(), sería más apropiado lanzar una señal (evento) cuando las cookies no sean válidas o no exista el archivo cookies.pkl. Luego, en el spider HistoriasClinicas, se puede definir un método para manejar la señal y realizar la solicitud de inicio de sesión en ese momento.

Aquí tienes una versión modificada del código teniendo en cuenta los puntos mencionados:
"""