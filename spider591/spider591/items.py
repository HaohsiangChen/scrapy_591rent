# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Rent591Item(scrapy.Item):
    house_id = scrapy.Field()
    city_name = scrapy.Field()
    owner = scrapy.Field()
    owner_type = scrapy.Field()
    owner_sex = scrapy.Field()
    price = scrapy.Field()
    phone_number = scrapy.Field()
    sex_limited = scrapy.Field()
    house_type = scrapy.Field()
    house_status = scrapy.Field()
    datetime = scrapy.Field()
