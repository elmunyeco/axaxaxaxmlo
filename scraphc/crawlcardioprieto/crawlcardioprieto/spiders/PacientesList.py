import scrapy
from .CookieHandler import CookieHandler


class PatientSpider(scrapy.Spider):
    name = 'patients'
    patients_url = "https://estudioadb.com/hc/index.php/pacientes/index"

    def start_requests(self):
        cookies = CookieHandler.load_cookies()
        if cookies is not None:
            yield scrapy.Request(url=self.patients_url, cookies=cookies, callback=self.parse_patients)

    def parse_patients(self, response):
        patients = response.css("table#dataTables-example tbody.tBody tr")
        for patient in patients:
            nombre = patient.css("td:nth-child(2)::text").get()
            apellido = patient.css("td:nth-child(3)::text").get()
            print(f"Nombre: {nombre}, Apellido: {apellido}")
