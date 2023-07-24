import scrapy
from .AuthenticatedSpider import AuthenticatedSpider
import time

class HistoriasClinicas(AuthenticatedSpider):
    name = 'hhcc'
    start_url = "https://estudioadb.com/hc/index.php/hClinica/index"


    def parse(self, response):
        print("EN EL PARSE")
        # Encuentra las filas de la tabla
        rows = response.xpath('//table[@id="dataTables-example"]/tbody/tr')

        for row in rows:
            # Extrae el valor del campo #1 (primer td)
            value = row.xpath('.//td[1]/text()').get()

            # Imprime el valor en la consola
            print(value)