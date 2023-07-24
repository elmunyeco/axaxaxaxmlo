import scrapy
import pickle
import os


class ListPatients(scrapy.Spider):
    name = "listpatients_aaa"
    login_url = "https://estudioadb.com/hc/index.php/login/validarUsuario"
    patients_url = "https://estudioadb.com/hc/index.php/pacientes/index"

    def start_requests(self):
        if os.path.exists("cookies.pkl"):
            with open("cookies.pkl", "rb") as f:
                cookies = pickle.load(f)
            return [
                scrapy.Request(
                    url=self.patients_url, cookies=cookies, callback=self.parse_patients
                )
            ]
        else:
            return [
                scrapy.FormRequest(
                    url=self.login_url,
                    formdata={"usuario": "omar", "pass": "Corbis5"},
                    callback=self.after_login,
                )
            ]

    def after_login(self, response):
        if response.css('li.dropdown a[href*="/login/logout"]'):
            with open("cookies.pkl", "wb") as f:
                pickle.dump(response.headers.getlist("Set-Cookie"), f)
            yield scrapy.Request(url=self.patients_url, callback=self.parse_patients)

    def parse_patients(self, response):
        patients = response.css("table#dataTables-example tbody.tBody tr")
        for patient in patients:
            nombre = patient.css("td:nth-child(2)::text").get()
            apellido = patient.css("td:nth-child(3)::text").get()
            print(f"Nombre: {nombre}, Apellido: {apellido}")
