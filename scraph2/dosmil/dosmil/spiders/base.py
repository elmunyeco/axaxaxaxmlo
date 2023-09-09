import os
import pickle
import scrapy
from scrapy.http import Request
from scrapy.exceptions import IgnoreRequest
from scrapy.utils.project import get_project_settings
from sortedcontainers import SortedDict
import csv

class CookieHandler:
    filename = "cookies.pkl"

    def __init__(self, logger):
        self.logger = logger

    def save_cookies(self, cookies):
        """Guarda las cookies en un archivo."""
        cookie_dict = {}
        for cookie in cookies:
            cookie_name, value = cookie.decode('utf-8').split(';', 1)[0].split('=', 1)
            cookie_dict[cookie_name] = value
        
        with open(self.filename, "wb") as f:
            pickle.dump(cookie_dict, f)
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

class AuthenticatedSpider(scrapy.Spider):

    # Credenciales y URL de login
    username = 'omar'
    password = 'Corbis5'
    login_url = 'https://estudioadb.com/hc/index.php/login/validarUsuario'
    start_urls = []
    
    # Gestor de cookies
    cookie_handler = CookieHandler(logger=scrapy.utils.log.logger)

    def is_logged_in(self, response):
        """Verifica si la respuesta indica un inicio de sesión exitoso."""
        return bool(response.css('li.dropdown a[href*="/login/logout"]'))

    def start_requests(self):
        cookies = self.cookie_handler.load_cookies()
        if cookies:
            yield Request(self.start_urls[0], cookies=cookies, callback=self.check_cookie, errback=self.handle_login_error)
        else:
            yield from self.login()

    def check_cookie(self, response):
        if not self.is_logged_in(response):
            self.logger.warning('Cookies inválidas o expiradas. Intentando relogueo.')
            yield from self.login()
        else:
            yield from self.parse(response)

    def login(self):
        """Hace una petición para loguearse."""
        yield scrapy.FormRequest(url=self.login_url, formdata={'usuario': self.username, 'pass': self.password}, callback=self.after_login)

    def after_login(self, response):
        if self.is_logged_in(response):
            cookies = response.headers.getlist('Set-Cookie')
            self.cookie_handler.save_cookies(cookies)
            yield Request(self.start_urls[0], callback=self.parse)
        else:
            self.logger.error('Error al loguearse.')

    def handle_login_error(self, failure):
        """Si hay un error, intenta loguearse nuevamente."""
        if failure.check(IgnoreRequest):
            self.logger.error('Fallo en Scrapy. Intentando relogueo.')
            yield from self.login()



import scrapy
from scrapy import Request
import csv
import os
from collections import OrderedDict as SortedDict

class PagedHistoriasClinicasSpider(AuthenticatedSpider):
    name = "paged_historias_clinicas"
    start_urls = ["https://estudioadb.com/hc/index.php/hClinica/index"]
    pages_url = "https://estudioadb.com/hc/index.php/hClinica/listar/"
    csv_file = "historias_clinicas.csv"

    def __init__(self, start_page=None, end_page=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records_to_write = self.load_existing_records()
        self.start_page = int(start_page) if start_page else 1
        self.end_page = int(end_page) if end_page else None
          
        
    def start_requests(self):
        cookies = self.cookie_handler.load_cookies()
        
        if not cookies:
            yield from self.login()
            return

        # Verifica si start_page es mayor que end_page
        if self.end_page and self.start_page > self.end_page:
            self.logger.error(f"start_page ({self.start_page}) es mayor que end_page ({self.end_page}). Abortando.")
            return
        
        if self.start_page and self.end_page:
            self.logger.info(f"Parseando páginas desde {self.start_page} hasta {self.end_page}...")
            for page in range(self.start_page, self.end_page + 1):
                yield Request(f"{self.pages_url}{page}", callback=self.parse_page)
        else: # Si no se proporciona una página final, se obtiene de la página de inicio
            self.logger.info("Parseando páginas desde la página de inicio...")
            yield Request(self.pages_url + "1", cookies=cookies, callback=self.parse_pagination, errback=self.handle_login_error)        

    def parse_pagination(self, response):
        self.logger.info("Entrando a parse_pagination...")
        # Escribe el contenido de la página a un archivo
        with open("raw.html", "w", encoding="utf-8") as file:
            file.write(response.text)    
    
        urls = response.css('ul.pagination li a::attr(href)').extract()
        if not urls:
            self.logger.error("No se encontró el paginador. Abortando.")
            return
        
        # Si no se especifica start_page, comenzar desde la primera página
        if not self.start_page:
            self.start_page = 1
            
        # Si no se especifica end_page, determinarlo a partir del paginador
        if not self.end_page:
            if len(urls) >= 2 and 'listar' in urls[-2]:
                self.end_page = int(urls[-2].split('/')[-1])
            else:
                # Cuando estamos en el último rango de páginas y los botones de "siguiente" no están presentes
                self.end_page = int(urls[-1].split('/')[-1])    
            
        for page in range(self.start_page, self.end_page + 1):
            yield Request(f"{self.pages_url}{page}", callback=self.parse_page)


    def parse_page(self, response):
        self.logger.info(f"Parseando página: {response.url}")
        
        #rows = response.xpath('//table[@id="dataTables-example"]/tbody/tr')
        #for row in rows:
        #    id_hc = row.xpath('.//td[1]/text()').get()
        #    nombre = row.xpath('.//td[2]/text()').get()
        #    apellido = row.xpath('.//td[3]/text()').get()
        #    self.records_to_write[id_hc] = {"nombre": nombre, "apellido": apellido}
        #    self.logger.info(f"ID: {id_hc}, Nombre: {nombre}, Apellido: {apellido}")
 

    def parse(self, response):
        pass

    def load_existing_records(self):
        if not os.path.exists(self.csv_file):
            return SortedDict()
        
        existing_records = SortedDict()
        with open(self.csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                existing_records[row[0]] = {"nombre": row[1], "apellido": row[2]}
        return existing_records

    def close_spider(self, spider):
        with open(self.csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Nombre", "Apellido"])  # Encabezados
            for id_hc, data in self.records_to_write.items():
                writer.writerow([id_hc, data['nombre'], data['apellido']])
