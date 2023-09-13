import scrapy

class EstudioadbSpider(scrapy.Spider):
    name = 'estudioadb'
    start_urls = ['http://estudioadb.com/hc/']

    def parse(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formdata={'usuario': 'omar', 'pass': 'Corbis5'},
            callback=self.after_login
        )
        
    def after_login(self, response):
        # Puede ser útil agregar una verificación de éxito de inicio de sesión aquí

        historia_clinica_url = 'http://estudioadb.com/hc/index.php/hClinica/index'
        yield scrapy.Request(historia_clinica_url, callback=self.parse_historia_clinica)
    
    def parse_historia_clinica(self, response):
        for row in response.css("table#dataTables-example tbody.tBody tr"):
            historia_clinica = row.css("td::text").get()
            nombre = row.css("td::text").extract()[1]
            apellido = row.css("td::text").extract()[2]
            documento = row.css("td::text").extract()[3]
            link_historia = row.css("td.center a::attr(href)").extract()[0] if row.css("td.center a::attr(href)").extract() else None
            link_estudios = row.css("td.center a::attr(href)").extract()[1] if len(row.css("td.center a::attr(href)").extract()) > 1 else None


            yield {
                'historia_clinica': historia_clinica,
                'nombre': nombre,
                'apellido': apellido,
                'documento': documento,
                'link_historia': link_historia,
                'link_estudios': link_estudios,
            }
            

        # Manejando paginación
        next_page = response.css("ul.pagination li a::attr(href)").extract()[-2]
        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse_historia_clinica)
