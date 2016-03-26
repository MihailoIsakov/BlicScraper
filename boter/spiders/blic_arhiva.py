import datetime

import scrapy
from scrapy import Request
from boter.items import Comment
import re

import logging
logger = logging.getLogger(__name__)


def _pad(number): 
    if number < 10:
        number = "0" + str(number)
    return number


def build_archive_link(year, month, day, pagination):
    return "http://www.blic.rs/archive/?s=%(pagination)s&date=%(year)s-%(month)s-%(day)s" \
        % {'year': year, 'month': _pad(month), 'day': _pad(day), 'pagination': pagination}


class BlicArhivaSpider(scrapy.Spider):
    name = "blic_arhiva"
    allowed_domains = ["blic.rs"]

    def start_requests(self):
        """
        Create a request for every days archive page.
        Each page is paginated, so a separate scrape is needed for every day.
        That scrape is the parse_archive_pagination method, which is called for
        the first page and calls itself for subsequent pages until it runs out
        of links.
        """
        _date = datetime.datetime.now()

        while _date.year > 2015:  # go through all the pages up to 2012
            # make the post request for the first page of that day's archive
            post = Request(
                build_archive_link(_date.year, _date.month, _date.day, 1),
                callback=self.parse_archive_pagination)
            post.meta['pagination'] = 1
            post.meta['date'] = _date
            yield post

            _date = _date - datetime.timedelta(1)  # tommorows date

    def parse_archive_pagination(self, response):
        """
        Go through the pages of the archive and scrape the article links
        until you stop finding articles to scrape.
        """
        articles = response.xpath('.//span[@class="archiveValue"]/a/@href')

        # if the current page has articles, look up the next one
        if len(articles) > 0: 
            pagination = response.meta['pagination']
            _date = response.meta['date']
            post = Request(
                build_archive_link(_date.year, _date.month, _date.day, pagination + 1),
                callback=self.parse_archive_pagination)
            post.meta['pagination'] = pagination + 1
            post.meta['date'] = _date
            yield post

        for article in articles:
            link = article.extract()
            post = Request(
                link,
                callback=self.parse_article)
            yield post

    def parse_article(self, response): 
        """Parses the page, finds the comment page link, goes there"""
        comment_page = response.xpath("//a[@class='k_makeComment']/@href")
        if len(comment_page) > 0: 
            comment_page = "http://www.blic.rs" + comment_page.extract()[0]
            return Request(comment_page, callback=self.parse_comment_page) 

    def parse_comment_page(self, response):
        comments = response.xpath('//div[contains(@class, "k_nForum_ReaderItem")]')
        #next_page = response.xpath('//a[contains(@class, "k_makeComment"]/@href')[0].extract() 
        #logger.info("Next page" + next_page)
        #yield Request(next_page, callback=self.parse_comment_page)

        logger.info(str(len(comments)) + " for " + response.url)

        for comment in comments:
            comment_id = comment.xpath('.//div[@class="k_commentHolder"]/@id').extract()[0]
            comment_id = re.findall(r"\d+", comment_id)[0]
            link = response.url
            author = comment.xpath('.//span[@class="k_author"]/text()').extract()[0].strip() 
            parent_author = comment.xpath('.//span[@class="k_parentAuthor"]/text()')
            if parent_author: 
                parent_author = parent_author.extract()[0].strip() 
            else: 
                parent_author = ""
            comment_text = comment.xpath(".//span[@class='k_content']/text()").extract()[0].strip()
            vote_count = comments.xpath(".//div[@class='k_nForum_MarkTipCount']/span/text()")[0].extract().strip()
            upvotes = comment.xpath(".//span[@class='k_nForum_MarkTipUpPercent']/text()")[0].extract().strip()
            downvotes = comment.xpath(".//span[@class='k_nForum_MarkTipDownPercent']/text()")[0].extract().strip()

            item = Comment()
            item['id'] = comment_id
            item['link'] = link
            item['author'] = author
            item['parent_author'] = parent_author
            item['comment'] = comment_text
            item['vote_count'] = vote_count
            item['upvotes'] = upvotes
            item['downvotes'] = downvotes

            yield item
