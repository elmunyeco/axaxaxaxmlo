import os
import pickle
from datetime import datetime


class CookieHandler:
    @staticmethod
    def load_cookies():
        if os.path.exists("cookies.pkl"):
            print("SI EXISTE EL ARCHIVO")
            with open("cookies.pkl", "rb") as f:
                cookies = pickle.load(f)
            return cookies
        else:
            print("LA CONCHADE TU MADRE NO EXISTE EL ARCHIVO")
            login_spider = LoginSpider()
            login_requests = login_spider.start_requests()
            # Esperar a que el spider LoginSpider complete antes de continuar
            yield from login_requests

    @staticmethod
    def save_cookies(cookies):
        print("GUARDANDO COOKIES")
        with open("cookies.pkl", "wb") as f:
            pickle.dump(cookies, f)

    @staticmethod
    def are_cookies_valid(cookies):
        if cookies is None:
            return False

        # Verificar si las cookies están en el formato esperado
        if not isinstance(cookies, dict):
            return False

        # Comprobar si las cookies tienen una fecha de expiración futura
        for cookie_name, cookie_value in cookies.items():
            if "expires" in cookie_value:
                expires_str = cookie_value["expires"]
                expires_datetime = datetime.strptime(
                    expires_str, "%a, %d-%b-%Y %H:%M:%S %Z"
                )
                if expires_datetime < datetime.now():
                    return False

        return True
