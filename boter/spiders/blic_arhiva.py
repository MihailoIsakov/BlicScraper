import scrapy
from scrapy import Request
from boter.items import Comment
from scrapy.shell import inspect_response

class BlicArhivaSpider(scrapy.Spider):
    name = "blic_arhiva"
    allowed_domains = ["blic.rs"]
    start_urls = (
        'http://www.blic.rs/arhiva',
    )

    def parse(self, response):
        archive = response.xpath('//*[@id="content_list_view"]/ul')
        archive_links = archive.xpath('.//@href')
        for link in archive_links:
            url = link.extract()
            if not BlicArhivaSpider._is_tracked(url):
                continue
            page_url = self._comment_page(url)
            yield Request(page_url, callback=self.parse_page )

    def parse_page(self, response):
        comments = response.xpath('//div[@db_id]')
        items = []
        for comment in comments:
            item = self._parse_comment(comment)
            items.append(item)

        return items

    @staticmethod
    def _parse_comment(comment):
        item = Comment()
        item['articleUrl'] = comment.xpath('//div[@id="main_content"]//h2[1]/a/text()').extract()
        item['comment']    = comment.xpath('.//div[@class="comm_text"]/text()').extract()
        item['upvotes']    = comment.xpath('.//span[@class="left"]/text()').extract()
        item['downvotes']  = comment.xpath('.//span[@class="comment_minus"]/text()').extract()

        commenterInfo = comment.xpath('.//div[@class="comm_u_name left"]')
        item['commenter'] = commenterInfo.xpath('span[1]/text()').extract()
        item['date'] = commenterInfo.xpath('span[2]/text()').extract()
        return item

    @staticmethod
    def _is_tracked(url):
        # tracked = ["Politika"]
        if "Politika" in url or "Ekonomija" in url:
            return True
        return False

    @staticmethod
    def _comment_page(url):
        return url + "/komentari#ostali"
