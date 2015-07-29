# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item

class Comment(Item):
    commenter = Field()
    comment = Field()
    upvotes = Field()
    downvotes = Field()
    date = Field()


class Page(Item):
    articleUrl = Field()
    articleName = Field()
    comments = Field()
