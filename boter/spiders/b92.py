# -*- coding: utf-8 -*-
import scrapy


class B92Spider(scrapy.Spider):
    name = "b92"
    allowed_domains = ["b92.net"]
    start_urls = (
        'http://www.b92.net/',
    )

    def parse(self, response):
        pass
