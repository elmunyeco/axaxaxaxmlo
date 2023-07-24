# myproject/spiders/authenticated_spider.py
import scrapy
from scrapy.http import Request
from scrapy.exceptions import IgnoreRequest
from .Login import LoginSpider as Login

class AuthenticatedSpider(scrapy.Spider):
    login_helper = None

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        spider.login_helper = Login(spider)
        return spider

    def start_requests(self):
        cookies = self.login_helper.get_cookies()
        yield Request(self.start_url, cookies=cookies, callback=self.parse, errback=self.handle_error)

    def parse(self, response):
        pass

    def handle_error(self, failure):
        if failure.check(IgnoreRequest):
            self.logger.error('Scrapy Fallado. Relogueando.')
            yield from self.login_helper.start_login()
