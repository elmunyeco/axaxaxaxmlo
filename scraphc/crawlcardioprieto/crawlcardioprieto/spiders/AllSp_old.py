from scrapy import Spider, Request
from scrapy import FormRequest
import pickle


class AllSp(Spider):
    name = "allsp_aaa"
    login_url = "https://estudioadb.com/hc/index.php/login/validarUsuario"
    start_urls = ["https://estudioadb.com/hc/index.php/login/validarUsuario"]
    patients_url = "https://estudioadb.com/hc/index.php/pacientes/index"

    def start_requests(self):
        # Intenta cargar las cookies de una ejecución anterior.
        try:
            with open("cookies.pkl", "rb") as f:
                cookies = pickle.load(f)
        except FileNotFoundError:
            cookies = None

        # Enviar una solicitud GET inicial con las cookies cargadas.
        yield Request(self.login_url, cookies=cookies, callback=self.login)

    def login(self, response):
        # Enviar una solicitud POST para iniciar sesión.
        return FormRequest.from_response(
            response,
            formdata={"usuario": "omar", "pass": "Corbis5"},
            callback=self.after_login,
        )

    def after_login(self, response):
        # Verificar si el inicio de sesión fue exitoso.
        if response.css('li.dropdown a[href*="/login/logout"]'):
            # Guardar todas las cookies en un archivo.
            with open("cookies.pkl", "wb") as f:
                pickle.dump(response.request.headers.getlist("Cookie"), f)

            # Ahora deberías llamar al spider de pacientes.
            yield Request(self.patients_url, callback=self.parse_patients)

    def parse_patients(self, response):
        patients = response.css("table#dataTables-example tbody.tBody tr")
        for patient in patients:
            nombre = patient.css("td:nth-child(2)::text").get()
            apellido = patient.css("td:nth-child(3)::text").get()
            print(f"Nombre: {nombre}, Apellido: {apellido}")
