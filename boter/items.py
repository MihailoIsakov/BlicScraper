# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item

class Comment(Item):
    id = Field()
    link = Field()
    author = Field()
    parent_author = Field()
    comment = Field()
    vote_count = Field()
    upvotes = Field()
    downvotes = Field()
