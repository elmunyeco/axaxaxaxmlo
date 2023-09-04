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

class PagedHistoriasClinicasSpider(AuthenticatedSpider):
    name = "paged_historias_clinicas"
    start_urls = ["https://estudioadb.com/hc/index.php/hClinica/index"]
    pages_url = "https://estudioadb.com/hc/index.php/hClinica/listar/"
    
    csv_file = "historias_clinicas.csv"

    # Continúa con la lógica específica para PagedHistoriasClinicasSpider...

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records_to_write = self.load_existing_records()
        
    def start_requests(self):
        cookies = self.cookie_handler.load_cookies()
        
        if cookies:
            # Si hay cookies, haz una solicitud a la URL de inicio para verificar si son válidas
            yield Request(self.start_urls[0], cookies=cookies, callback=self.check_cookie, errback=self.handle_login_error)
        else:
            # Si no hay cookies, inicia sesión
            yield from self.login()

        page_number = getattr(self, 'page', None)
        if page_number is None or page_number == 'all':
            self.logger.info ("HAY QUE ITERAR POR TODAS LAS PAGINAS")
            yield from self.iterate_through_pages(cookies) # Pasa las cookies como argumento
        else:
            self.logger.info ("HAY QUE ITERAR POR UNA PAGINA ESPECIFICA")
            yield Request(f"{self.pages_url}{page_number}", cookies=cookies, callback=self.parse, meta={'cookies': cookies})
            
    def iterate_through_pages(self, cookies):
        start_page = 1
        end_page = 2 
        
        if cookies is None or not self.check_cookie(response):
            self.logger.error('No se encontraron cookies o están expiradas.')
            yield from self.login()    
    
        for page in range(start_page, end_page + 1):
            yield Request(f"{self.pages_url}{page}", cookies=cookies, callback=self.parse, meta={'cookies': cookies})
    
    # Archivo CSV donde se escribirán los datos    
    
    def parse(self, response):
        cookies = response.meta.get('cookies')  # Obtiene las cookies del meta
        if cookies is None or not self.check_cookie(response):
            self.logger.error('No se encontraron cookies o están expiradas.')
            yield from self.login()    
        
        raw_html = response.body.decode(response.encoding)
        self.logger.info(f"Raw Raw RawRawRawRawRawRawRawRaw Raw Raw Raw RawHTML: {raw_html}")
        
        rows = response.xpath('//table[@id="dataTables-example"]/tbody/tr')
        for row in rows:
            field1 = row.xpath('.//td[1]/text()').get()
            field2 = row.xpath('.//td[2]/text()').get()
            self.records_to_write[field1] = field2  # Agregar al SortedDict

            self.logger.info(f"Campo 1: {field1}, Campo 2: {field2}")
            
        self.print_formatted_rows(rows)  # Impresión formateada de rows
        
        # Write to the CSV file
        with open(self.csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for field1, field2 in self.records_to_write.items():
                writer.writerow([field1, field2])
  # Impresión formateada de rows
    
        with open(self.csv_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for field1, field2 in records_to_write.items():
                writer.writerow([field1, field2])

    def print_formatted_rows(self, rows):
        for index, row in enumerate(rows, start=1):
            field1 = row.xpath('.//td[1]/text()').get()
            field2 = row.xpath('.//td[@class="center"]/a/@href').get()
            self.logger.info(f"Formatted Row {index}: Campo 1: {field1}, Campo 2: {field2}")
 
        # Devuelve una lista vacía
        return []
    
    def load_existing_records(self):
        full_path = os.path.abspath(self.csv_file)
        self.logger.info(f"Cargando registros existentes desde: {full_path}")
        
        if not os.path.exists(self.csv_file):
            return SortedDict()
        
        existing_records = SortedDict()
        with open(self.csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                existing_records[row[0]] = row[1]
        return existing_records


    
    def parse(self, response):
        cookies = response.meta.get('cookies')  # Obtiene las cookies del meta
        if cookies is None or not self.check_cookie(response):
            self.logger.error('No se encontraron cookies o están expiradas.')
            yield from self.login()    
        
        raw_html = response.body.decode(response.encoding)
        self.logger.info(f"Raw Raw RawRawRawRawRawRawRawRaw Raw Raw Raw RawHTML: {raw_html}")
        
        rows = response.xpath('//table[@id="dataTables-example"]/tbody/tr')
        for row in rows:
            field1 = row.xpath('.//td[1]/text()').get()
            field2 = row.xpath('.//td[2]/text()').get()
            self.records_to_write[field1] = field2  # Agregar al SortedDict

            self.logger.info(f"Campo 1: {field1}, Campo 2: {field2}")
            
        self.print_formatted_rows(rows)  # Impresión formateada de rows
        
        # Write to the CSV file
        with open(self.csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for field1, field2 in self.records_to_write.items():
                writer.writerow([field1, field2])
  # Impresión formateada de rows

    
    def close_spider(self, spider):
        full_path = os.path.abspath(self.csv_file)
        self.logger.info(f"Escribiendo registros en: {full_path}")
        
        with open(self.csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for field1, field2 in self.records_to_write.items():
                writer.writerow([field1, field2])


    