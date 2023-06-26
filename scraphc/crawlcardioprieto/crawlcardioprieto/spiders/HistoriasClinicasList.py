import scrapy
from .CookieHandler import CookieHandler
from .Login import LoginSpider

class HistoriasClinicas(scrapy.Spider):
    name = 'hhcc'
    start_urls = ["https://estudioadb.com/hc/index.php/hClinica/index"]

    def start_requests(self):
        cookies = CookieHandler.load_cookies()
        if cookies is not None:
            yield scrapy.Request(url=self.start_urls[0], cookies=cookies, callback=self.parse_hhcc)
        else:
            # No hay cookies guardadas, se redirige al spider LoginSpider para iniciar sesión
            login_spider = LoginSpider()
            yield from login_spider.start_requests()

    def parse_hhcc(self, response):
        # Encuentra las filas de la tabla
        rows = response.xpath('//table[@id="dataTables-example"]/tbody/tr')

        for row in rows:
            # Extrae el valor del campo #1 (primer td)
            value = row.xpath('.//td[1]/text()').get()

            # Imprime el valor en la consola
            print(value)
