import os
import pickle

class CookieHandler:

    @staticmethod
    def load_cookies():
        print ('ADENTRO DE LOAD COOKIE')
        if os.path.exists('cookies.pkl'):
            print ('SI EXISTE EL ARCHIVO')
            with open('cookies.pkl', 'rb') as f:
                cookies = pickle.load(f)
            return cookies
        else:
            print ('LA CONCHADE TU MADRE NO EXISTE EL ARCHIVO')
            return None

    @staticmethod
    def save_cookies(cookies):
        with open('cookies.pkl', 'wb') as f:
            pickle.dump(cookies, f)
