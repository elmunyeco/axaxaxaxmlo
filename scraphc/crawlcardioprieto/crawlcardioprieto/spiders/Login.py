import scrapy
from .CookieHandler import CookieHandler

class LoginSpider(scrapy.Spider):
    name = 'login'
    login_url = e

    def start_requests(self):
        cookies = CookieHandler.load_cookies()
        if cookies is not None:
            yield scrapy.Request(url=self.login_url, cookies=cookies, callback=self.after_login)
        else:
            yield scrapy.FormRequest(url=self.login_url, formdata={'usuario': 'omar', 'pass': 'Corbis5'}, callback=self.after_login)

    def after_login(self, response):
        if response.css('li.dropdown a[href*="/login/logout"]'):
            cookies = response.headers.getlist('Set-Cookie')
            CookieHandler.save_cookies(cookies)
