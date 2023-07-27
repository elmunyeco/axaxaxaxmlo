import os
import pickle
import scrapy
from scrapy import Spider
from abc import ABC, abstractmethod  # Importa abstractmethod desde el módulo abc
from scrapy.http import Request
from scrapy.exceptions import IgnoreRequest


# Gestor de cookies para guardarlas y cargarlas desde un archivo
class CookieHandler:
    filename = "cookies.pkl"

    def __init__(self, logger):
        self.logger = logger

    def save_cookies(self, cookies):
        """Guarda las cookies en un archivo."""
        with open(self.filename, "wb") as f:
            pickle.dump(cookies, f)
        self.logger.info('Cookies guardadas en el archivo.')

    def load_cookies(self):
        """Carga las cookies desde un archivo, si existe."""
        if os.path.exists(self.filename):
            with open(self.filename, "rb") as f:
                cookies = pickle.load(f)
                self.logger.info('Cookies cargadas desde el archivo.')
                return cookies
        else:
            self.logger.warning('Archivo de cookies no encontrado.')
            return None

class AuthenticatedSpider(scrapy.Spider, ABC):
    # Credenciales y URL de login
    username = 'omar'
    password = 'Corbis5'
    login_url = 'https://estudioadb.com/hc/index.php/login/validarUsuario'
    
    # Gestor de cookies
    cookie_handler = CookieHandler(logger=scrapy.utils.log.logger)

    def start_requests(self):
        """Inicia las solicitudes. Si existen cookies, las usa. Si no, se loguea."""
        cookies = self.cookie_handler.load_cookies()
        if cookies is not None:
            yield Request(self.start_url, cookies=cookies, callback=self.check_cookie, errback=self.handle_login_error)
        else:
            yield from self.login()

    def check_cookie(self, response):
        """Verifica si la respuesta indica un inicio de sesión exitoso o si las cookies se cargaron desde el archivo."""
        cookies = self.cookie_handler.load_cookies()
        if cookies is not None:
            # Las cookies se cargaron desde el archivo, continuar con el análisis de la página
            yield from self.parse(response)
        else:
            # Verificar si el inicio de sesión fue exitoso
            if response.css('li.dropdown a[href*="/login/logout"]'):
                yield from self.parse(response)
            else:
                self.logger.warning('Cookies inválidas o expiradas. Intentando relogueo.')
                yield from self.login()
                
    def login(self):
        """Hace una petición para loguearse."""
        yield scrapy.FormRequest(url=self.login_url, formdata={'usuario': self.username, 'pass': self.password}, callback=self.after_login)

    def after_login(self, response):
        """Guarda las cookies después del login y continua con el inicio."""
        if response.css('li.dropdown a[href*="/login/logout"]'):
            cookies = response.headers.getlist('Set-Cookie')
            cookie_dict = {cookie.decode('utf-8').split('=', 1)[0]: cookie.decode('utf-8').split('=', 1)[1] for cookie in cookies}
            self.cookie_handler.save_cookies(cookie_dict)
            yield Request(self.start_url, cookies=cookie_dict, callback=self.parse)
        else:
            self.logger.error('Error al loguearse.')

    def handle_login_error(self, failure):
        """Si hay un error, intenta loguearse nuevamente."""
        if failure.check(IgnoreRequest):
            self.logger.error('Fallo en Scrapy. Intentando relogueo.')
            yield from self.login()

class HistoriasClinicasSpider(AuthenticatedSpider):
    name = "historias_clinicas"
    start_url = "https://estudioadb.com/hc/index.php/hClinica/index"

    def parse(self, response):
        """Extrae e imprime el valor del primer campo de cada fila en la tabla de historias clínicas."""
        rows = response.xpath('//table[@id="dataTables-example"]/tbody/tr')
        for row in rows:
            value = row.xpath('.//td[1]/text()').get()
            self.logger.info(f"Valor extraído: {value}")

        # Aquí debes devolver un objeto iterable, por ejemplo, una lista vacía.
        return []