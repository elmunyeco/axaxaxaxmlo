import os
import pickle
import scrapy
import csv
from scrapy import Spider
from abc import ABC, abstractmethod  # Importa abstractmethod desde el módulo abc
from scrapy.http import Request
from scrapy.exceptions import IgnoreRequest

import sys
from scrapy.utils.project import get_project_settings



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
    csv_file = "historias_clinicas.csv"


    # Archivo CSV donde se escribirán los datos    
    def parse(self, response):
        """Extrae los valores de los campos especificados de cada fila en la tabla de historias clínicas y los escribe en un archivo CSV."""
        rows = response.xpath('//table[@id="dataTables-example"]/tbody/tr')
        
        # Abre el archivo CSV en modo append
        with open(self.csv_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            for row in rows:
                field1 = row.xpath('.//td[1]/text()').get()
                field2 = row.xpath('.//td[@class="center"]/a/@href').get()
                
                # Escribe los campos en el archivo CSV
                writer.writerow([field1, field2])

                # Imprime los campos en la consola
                self.logger.info(f"Campo 1: {field1}, Campo 2: {field2}")

        # Devuelve una lista vacía
        return []
    
class PagedHistoriasClinicasSpider(AuthenticatedSpider):
    name = "paged_historias_clinicas"
    start_url = "https://estudioadb.com/hc/index.php/hClinica/index"
    pages_url = "https://estudioadb.com/hc/index.php/hClinica/listar/"
    
    csv_file = "historias_clinicas.csv"

    def start_requests(self):
        
        yield from super().start_requests()  # Siempre inicia el proceso de autenticación

        page_number = getattr(self, 'page', None)
        
        if page_number is None or page_number == 'all':
            self.logger.info ("LA CONCHA DE TU MAAAAAAAAAAAAAAAAAAAAAAAAAAAADREEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
            yield from self.iterate_through_pages()
        else:
            self.logger.info ("LA PUTAQUE TE HIZOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
            yield Request(f"{self.pages_url}{page_number}", callback=self.parse)
            """yield from super().start_requests()"""
            
    def iterate_through_pages(self):
        start_page = 1
        end_page = 2  # You can adjust the end page as needed
        for page in range(start_page, end_page + 1):
            yield Request(f"{self.pages_url}{page}", callback=self.parse)


    # Archivo CSV donde se escribirán los datos    
    def parse(self, response):
        """Extrae los valores de los campos especificados de cada fila en la tabla de historias clínicas y los escribe en un archivo CSV."""
        rows = response.xpath('//table[@id="dataTables-example"]/tbody/tr')
      
        # Abre el archivo CSV en modo append
        with open(self.csv_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            for row in rows:
                field1 = row.xpath('.//td[1]/text()').get()
                field2 = row.xpath('.//td[@class="center"]/a/@href').get()
                
                # Escribe los campos en el archivo CSV
                writer.writerow([field1, field2])

                # Imprime los campos en la consola
                self.logger.info(f"Campo 1: {field1}, Campo 2: {field2}")

        # Devuelve una lista vacía
        return []