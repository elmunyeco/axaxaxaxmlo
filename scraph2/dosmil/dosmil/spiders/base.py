import os
import pickle
import scrapy
from scrapy.http import Request
from scrapy.exceptions import IgnoreRequest


class CookieHandler:
    filename = "cookies.pkl"

    def save_cookies(self, cookies):
        print("GUARDANDO COOKIES")
        with open(self.filename, "wb") as f:
            pickle.dump(cookies, f)

    def load_cookies(self):
        print("CARGANDO COOKIES")
        if os.path.exists(self.filename):
            with open(self.filename, "rb") as f:
                return pickle.load(f)
        else:
            print("LA CONCHADE TU MADRE NO EXISTE EL ARCHIVO")
            return None

class AuthenticatedSpider(scrapy.Spider):
    username = 'omar'
    password = 'Corbis5'
    login_url = 'https://estudioadb.com/hc/index.php/login/validarUsuario'
    cookie_handler = CookieHandler()

    def start_requests(self):
        cookies = self.cookie_handler.load_cookies()
        if cookies is not None:
            yield Request(self.start_url, cookies=cookies, callback=self.parse, errback=self.handle_login_error)
        else:
            yield from self.login()

    def login(self):
        yield scrapy.FormRequest(url=self.login_url, formdata={'usuario': self.username, 'pass': self.password}, callback=self.after_login)

    def after_login(self, response):
        if response.css('li.dropdown a[href*="/login/logout"]'):
            cookies = {c.name: c.value for c in response.request.cookies}
            # cookies = response.headers.getlist('Set-Cookie')
            self.cookie_handler.save_cookies(cookies)
            yield Request(self.start_url, cookies=cookies, callback=self.parse)
        else:
            self.logger.error('ERROR AL LOGUEARSE')

    def handle_login_error(self, failure):
        if failure.check(IgnoreRequest):
            self.logger.error('Scrapy Fallado. Relogueando.')
            yield from self.login()

    # Aquí es donde tu spider concreta procesaría las respuestas HTTP.
    def parse(self, response):
        pass

class HistoriasClinicasSpider(AuthenticatedSpider):
    name = "historias_clinicas"
    start_url = "https://estudioadb.com/hc/index.php/hClinica/index"

    def parse(self, response):
        rows = response.xpath('//table[@id="dataTables-example"]/tbody/tr')

        for row in rows:
            # Extrae el valor del campo #1 (primer td)
            value = row.xpath('.//td[1]/text()').get()

            # Imprime el valor en la consola
            print(value)