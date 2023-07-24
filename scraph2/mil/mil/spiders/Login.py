import scrapy
import pickle
import os

# from .CookieHandler import CookieHandler

class LoginSpider(scrapy.Spider):
    login_url =  'https://estudioadb.com/hc/index.php/login/validarUsuario'
    username = 'omar'
    password = 'Corbis5'

    def __init__(self, spider):
        self.spider = spider
        
    def start_login(self):
        data = {
            'usuario': self.username, 
            'pass': self.password
        }
        return scrapy.FormRequest(url=self.login_url, formdata=data, callback=self.after_login)    
    
    def start_requests(self):
        cookies = get_cookies()
        if cookies is not None:
            yield scrapy.Request(url=self.login_url, cookies=cookies, callback=self.after_login)
        else:
            yield scrapy.FormRequest(url=self.login_url, formdata={'usuario': 'omar', 'pass': 'Corbis5'}, callback=self.after_login)

    def after_login(self, response):
        if response.css('li.dropdown a[href*="/login/logout"]'):
            self.cookies = response.headers.getlist('Set-Cookie')
            self.save_cookies(self.cookies)
        else:
            self.spider.logger.error('ERROR AL LOGUEARSE')
            return

    def save_cookies(self, cookies):
        print("GUARDANDO COOKIES")
        with open("cookies.pkl", "wb") as f:
            pickle.dump(cookies, f)
            
    def get_cookies(self):
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