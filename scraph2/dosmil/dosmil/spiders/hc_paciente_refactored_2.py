import scrapy
import re
from scrapy.exceptions import CloseSpider

class EstudioadbSpider(scrapy.Spider):
    name = 'hc_paciente_refactored_2'
    start_urls = ['http://estudioadb.com/hc/']

    def __init__(self, hc_ids=None, *args, **kwargs): 
        super(EstudioadbSpider, self).__init__(*args, **kwargs)
        self.hc_ids = hc_ids.split(",") if hc_ids else []
        self.hc_id = None
        self.current_task = None
        self.task_queue = []

    def parse(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formdata={'usuario': 'omar', 'pass': 'Corbis5'},
            callback=self.after_login
        )

    def after_login(self, response):
        if self.hc_ids:
            self.hc_id = self.hc_ids.pop(0)
            self.initiate_task_queue()
            self.process_next_task()
        else:
            # Procesar sin hc_ids especificados
            pass

    def initiate_task_queue(self):
        patient_details_url = f"http://estudioadb.com/hc/index.php/pacientes/editar/{self.hc_id}"
        historia_clinica_details_url = f"http://estudioadb.com/hc/index.php/hClinica/verHClinica/{self.hc_id}"

        self.task_queue = [
            {'url': patient_details_url, 'callback': self.parse_patient_details},
            {'url': historia_clinica_details_url, 'callback': self.parse_historia_clinica_details}
        ]

    def process_next_task(self):
        if self.task_queue:
            task = self.task_queue.pop(0)
            self.current_task = task
            yield scrapy.Request(url=task['url'], callback=task['callback'], meta={'historia_clinica': self.hc_id})
        else:
            if self.hc_ids:
                self.after_login(None)  # Procesa el siguiente hc_id
            else:
                # Fin del proceso
                pass

    # Métodos parse y extract como en tu versión original

    def parse_patient_details(self, response):
        historia_clinica = response.meta['historia_clinica']
        detalle = {
            'tipo': 'detalle_paciente',
            'historia_clinica': historia_clinica,
            "Tipo de Documento": response.css("#tipoDoc option[selected='selected']::text").get(),
            "N° Documento": response.css("#numDoc::attr(value)").get().strip(),
            "Nombre": response.css("#nombre::attr(value)").get().strip(),
            "Apellido": response.css("#apellido::attr(value)").get().strip(),
            "Fecha de Nacimiento": response.css("#fechaNac::attr(value)").get().strip(),
            "Sexo": "Hombre" if response.css("input[name='sexo'][value='H'][checked='checked']") else "Mujer" if response.css("input[name='sexo'][value='M'][checked='checked']") else None,
            "Email": response.css("#email::attr(value)").get().strip(),
            "Dirección": response.css("#direccion::attr(value)").get().strip(),
            "Localidad": response.css("#localidad::attr(value)").get().strip(),
            "Obra Social": response.css("#obraSocial::attr(value)").get().strip(),
            "Plan": response.css("#plan::attr(value)").get().strip(),
            "N° Afiliado": response.css("#afiliado::attr(value)").get().strip(),
            "Teléfono": response.css("#telefono::attr(value)").get().strip(),
            "Celular": response.css("#celular::attr(value)").get().strip(),
            "Profesión": response.css("#profesion::attr(value)").get().strip(),
            "Médico Referente": response.css("#referente::attr(value)").get().strip(),
        }        yield detalle
        self.process_next_task()

    def parse_historia_clinica_details(self, response):
        historia_clinica_data = {
            'tipo': 'detalle_historia_clinica',
            'historia_clinica': response.meta.get('historia_clinica'),
            'diagnosticos': self.extract_diagnosticos(response),
            'visitas': self.extract_visitas(response),
                #'fechas_comentarios': self.extract_fecha_visitas(respnse),
                #'comentarios': self.extract_visita_comentarios(response),
                #'signos_vitales': self.extract_visita_signos_vitales(response),
                #'medicamentos': self.extract_visita_medicamentos(response),
                #'comentario_medicamentos': self.extract_visita_comentario_medicamentos(response)

            # Aquí puedes agregar más extractores para otros paneles.
        }        
        yield historia_clinica_data
        self.process_next_task()
        
    def extract_diagnosticos(self, response):
        diagnosticos = {}
        for checkbox in response.css("div.form-group.center div.col-xs-4 input"):
            enfermedad = checkbox.xpath("./following-sibling::text()").get().strip()
            is_checked = checkbox.xpath("./@checked").get() == "checked"
            diagnosticos[enfermedad] = is_checked
        
        return diagnosticos

    # Al dope
    def extract_signos_vitales(self, response):    
        signos_vitales = {}

        # Extrayendo los signos vitales
        signos_vitales['Peso'] = response.css('input#peso::attr(value)').extract_first()
        signos_vitales['Colesterol'] = response.css('input#colesterol::attr(value)').extract_first()
        signos_vitales['Glucemia'] = response.css('input#glucemia::attr(value)').extract_first()
        signos_vitales['PAS'] = response.css('input#presionSistolica::attr(value)').extract_first()
        signos_vitales['PAD'] = response.css('input#presionDiastolica::attr(value)').extract_first()

        return signos_vitales


    def extract_visitas(self, response):
        data = []
        visitas = response.css("div.panel.panel-red")
        
        for visita in visitas:
            item = {
                'fecha': self.extract_visita_fecha(visita),
                'comentarios': self.extract_visita_comentarios(visita),
                'signos_vitales': self.extract_visita_signos_vitales(visita),
                'medicamentos': self.extract_visita_medicamentos(visita),
                'comentario_medicamentos': self.extract_visita_comentario_medicamentos(visita)
            }
            
            data.append(item)
        
        return data
        
    
    def extract_visita_fecha (self, visita):
        fecha = visita.css("div.panel-heading h4 a::text").get().strip()
        
        return fecha
        
    def extract_visita_comentarios(self, visita):
        comentarios = visita.css("div.divComentario::text").extract()
        return [comentario.strip() for comentario in comentarios if comentario and comentario.strip()]

    def extract_visita_signos_vitales(self, visita):
        signos = {}
        items = visita.css("ul.listSignosVitales > li")
        for item in items:
            key = item.css("span.col-lg-6:nth-child(1)::text").get(default="").strip()
            value = item.css("span.col-lg-6:nth-child(2)::text").get(default="").strip()
            if key:
                signos[key] = value
        return signos

    def extract_visita_medicamentos(self, visita):
        medicamentos = []
        rows = visita.css("tbody.tBody > tr")
        for row in rows:
            medicamento = row.css("td:nth-child(1)::text").get(default="").strip()
            dosis = {
                "08:00 hs": row.css("td:nth-child(2)::text").get(default="").strip(),
                "12:00 hs": row.css("td:nth-child(3)::text").get(default="").strip(),
                "18:00 hs": row.css("td:nth-child(4)::text").get(default="").strip(),
                "21:00 hs": row.css("td:nth-child(5)::text").get(default="").strip()
            }
            if medicamento:
                medicamentos.append({"medicamento": medicamento, "dosis": dosis})
        return medicamentos

    def extract_visita_comentario_medicamentos(self, visita):
        return visita.css("textarea#comentario::text").get(default="").strip()
