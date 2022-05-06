# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class ManhuaItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    cartoon_type = Field()
    cartoon_url = Field()

    next_name = Field()
    serialize = Field()
    sub_type = Field()
    next_book_url = Field()
    next_image_url = Field()

    describe = Field()
    book_url = Field()
    image_url = Field()
