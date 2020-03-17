# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import Join, MapCompose, TakeFirst
from w3lib.html import remove_tags


def clear_string(text):
    text = "".join(text.strip())
    return text


class UludagtutorialItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field(
        input_processor=MapCompose(remove_tags, clear_string),
        output_processor=Join()
    )
    comment = scrapy.Field(
        input_processor=MapCompose(remove_tags, clear_string),
        output_processor=Join()
    )

    user = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=Join(separator=u', ')
    )

    user_detail = scrapy.Field(
        input_processor=TakeFirst(),
        output_processor=TakeFirst()
    )

    date = scrapy.Field(
        input_processor=MapCompose(remove_tags, clear_string),
        output_processor=TakeFirst()
    )
    url = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=TakeFirst()
    )

