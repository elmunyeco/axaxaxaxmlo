import scrapy
from scrapy.exceptions import CloseSpider   

class EstudioadbSpider(scrapy.Spider):
    name = 'estudioadb'
    start_urls = ['http://estudioadb.com/hc/']

    def __init__(self, *args, **kwargs): 
        super(EstudioadbSpider, self).__init__(*args, **kwargs)
        self.pages_crawled = 0
        self.hc_crawled = 0
        self.pacientes_crawled = 0

    def parse(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formdata={'usuario': 'omar', 'pass': 'Corbis5'},
            callback=self.after_login
        )
        
    def after_login(self, response):
        historia_clinica_url = 'http://estudioadb.com/hc/index.php/hClinica/index'
        yield scrapy.Request(historia_clinica_url, callback=self.parse_historia_clinica)
    
    def parse_historia_clinica(self, response):
        for row in response.css("table#dataTables-example tbody.tBody tr"):
            historia_clinica = row.css("td::text").extract()[0]
            nombre = row.css("td::text").extract()[1]
            apellido = row.css("td::text").extract()[2]
            documento = row.css("td::text").extract()[3]
            link_historia = row.css("td.center a::attr(href)").extract()[0] if row.css("td.center a::attr(href)").extract() else None
            link_estudios = row.css("td.center a::attr(href)").extract()[1] if len(row.css("td.center a::attr(href)").extract()) > 1 else None

            if self.hc_crawled < 1:
                yield {
                    'tipo': 'historia_clinica',
                    'historia_clinica': historia_clinica,
                    'nombre': nombre,
                    'apellido': apellido,
                    'documento': documento,
                    'link_historia': link_historia,
                    'link_estudios': link_estudios
                }

                # Extracting patient details link
                patient_details_url = response.urljoin(f"/hc/index.php/pacientes/editar/{historia_clinica}")
                yield scrapy.Request(url=patient_details_url, callback=self.parse_patient_details, meta={'historia_clinica': historia_clinica})

                # Extracting historia clinica details
                historia_clinica_details_url = response.urljoin(link_historia)
                yield scrapy.Request(url=historia_clinica_details_url, callback=self.parse_historia_clinica_details, meta={'historia_clinica': historia_clinica})

                self.hc_crawled += 1
                             
        # Manejando paginación
        if self.pages_crawled < 1:
            next_page = response.css("ul.pagination li a::attr(href)").extract()[-2]
            if next_page:
                self.pages_crawled += 1
                yield scrapy.Request(url=next_page, callback=self.parse_historia_clinica)

    def parse_patient_details(self, response):
        historia_clinica = response.meta['historia_clinica']

        detalle = {
            'tipo': 'detalle_paciente',
            'historia_clinica': historia_clinica,
            "Tipo de Documento": response.css("#tipoDoc option[selected='selected']::text").get(),
            "N° Documento": response.css("#numDoc::attr(value)").get(),
            "Nombre": response.css("#nombre::attr(value)").get(),
            "Apellido": response.css("#apellido::attr(value)").get(),
            "Fecha de Nacimiento": response.css("#fechaNac::attr(value)").get(),
            "Sexo": "Hombre" if response.css("input[name='sexo'][value='H'][checked='checked']") else "Mujer" if response.css("input[name='sexo'][value='M'][checked='checked']") else None,
            "Email": response.css("#email::attr(value)").get(),
            "Dirección": response.css("#direccion::attr(value)").get(),
            "Localidad": response.css("#localidad::attr(value)").get(),
            "Obra Social": response.css("#obraSocial::attr(value)").get(),
            "Plan": response.css("#plan::attr(value)").get(),
            "N° Afiliado": response.css("#afiliado::attr(value)").get(),
            "Teléfono": response.css("#telefono::attr(value)").get(),
            "Celular": response.css("#celular::attr(value)").get(),
            "Profesión": response.css("#profesion::attr(value)").get(),
            "Médico Referente": response.css("#referente::attr(value)").get(),
        }
        
        
        yield detalle
    
    def parse_historia_clinica_details(self, response):
        historia_clinica_data = {
            'tipo': 'detalle_historia_clinica',
            'historia_clinica': response.meta.get('historia_clinica'),
            'datos_paciente': self.extract_patient_data(response),
            'diagnosticos': self.extract_diagnosticos(response),
            # Aquí puedes agregar más extractores para otros paneles.
        }
        
        yield historia_clinica_data

    def extract_patient_data(self, response):
        data = {}
        # Datos de la columna izquierda
        #OHIGGINS ESTO!!!!! body > div.mainContainer > div.main.col-lg-10 > div > div > div.panel-body > div:nth-child(1) > div:nth-child(1) > div.panel.panel-default > div.panel-body.form-horizontal.boxPaciente > div:nth-child(1) > div:nth-child(1)
        data['Tipo Doc.'] = response.css(".boxPaciente .col-lg-6:nth-child(1) div:nth-child(1)::text").extract_first().strip()
        data['Nombre'] = response.css(".boxPaciente .col-lg-6:nth-child(1) div:nth-child(2)::text").extract_first().strip()
        data['O. Social'] = response.css(".boxPaciente .col-lg-6:nth-child(1) div:nth-child(3)::text").extract_first().strip()
        data['Tel'] = response.css(".boxPaciente .col-lg-6:nth-child(1) div:nth-child(4)::text").extract_first().strip()
        data['Fec. Nac.'] = response.css(".boxPaciente .col-lg-6:nth-child(1) div:nth-child(5)::text").extract_first().strip()

        # Datos de la columna derecha
        data['N° Doc.'] = response.css(".boxPaciente .col-lg-6:nth-child(2) div:nth-child(1)::text").extract_first().strip()
        data['Apellido'] = response.css(".boxPaciente .col-lg-6:nth-child(2) div:nth-child(2)::text").extract_first().strip()
        data['N° Afiliado'] = response.css(".boxPaciente .col-lg-6:nth-child(2) div:nth-child(3)::text").extract_first().strip()
        data['Celular'] = response.css(".boxPaciente .col-lg-6:nth-child(2) div:nth-child(4)::text").extract_first().strip()
        data['Email'] = response.css(".boxPaciente .col-lg-6:nth-child(2) div:nth-child(5)::text").extract_first().strip()

        return data

    def extract_diagnosticos(self, response):
        diagnosticos = {}
        for checkbox in response.css("div.form-group.center div.col-xs-4 input"):
            enfermedad = checkbox.xpath("./following-sibling::text()").get().strip()
            is_checked = checkbox.xpath("./@checked").get() == "checked"
            diagnosticos[enfermedad] = is_checked
        
        return diagnosticos

    # Agregar aquí métodos extract_* adicionales para otros paneles.
