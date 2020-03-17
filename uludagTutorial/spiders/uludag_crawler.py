import scrapy
from scrapy.loader import ItemLoader
from ..items import UludagtutorialItem
from .util import ulu_db
from hashlib import sha256
import json


def encode_item(loader_item):
    return sha256(json.dumps(loader_item, sort_keys=True).encode('utf8')).hexdigest()


class UludagCrawler(scrapy.Spider):
    name = 'uludag'
    page_number = 1

    allowed_domains = ["www.uludagsozluk.com"]
    start_urls = [
        'https://www.uludagsozluk.com/index.php?sa=gundem&sp=1'
    ]

    def parse(self, response):

        title_urls = response.xpath("//ul[@class='index-list']/li/a")
        # If program has reached the end of the gündem's page, stop.
        if title_urls.extract_first() is None:
            # TODO: for making infinite to program, it must return the beginning from here when it reaches here.
            return

        for t_url in title_urls:
            title_url = t_url.xpath(".//@href").extract_first()
            if "//uludagsozluk.com" in title_url:
                title_url = title_url.replace("//uludagsozluk.com", "")

            title_name = t_url.xpath(".//text() | .//a/text()").extract_first()
            abs_url = "https://www.uludagsozluk.com" + title_url
            yield scrapy.Request(abs_url, callback=self.parse_detail, meta={'title_name': title_name})

        self.page_number += 1
        next_url = "https://www.uludagsozluk.com/index.php?sa=gundem&sp={}".format(self.page_number)
        yield scrapy.Request(next_url,
                             callback=self.parse,
                             dont_filter=True)

    def parse_detail(self, response):
        t_name = response.xpath("//h1/a/text()").extract_first()
        for post in response.xpath("//li[@class='li_capsul_entry']"):
            l = ItemLoader(item=UludagtutorialItem(), selector=post)
            l.add_value("title", response.meta.get('title_name', t_name))
            l.add_xpath("comment", ".//div[@class='entry-p']/text() | .//div[@class='entry-p']/a/text()")
            l.add_xpath("user", ".//div[@class='entry-secenekleri']/a[@class='alt-u yazar']/text()")
            l.add_xpath("date", ".//span[@class='date-u']/a/text()")
            l.add_xpath("url", "substring-after(.//div[@class='voting_nw']/a/@href, '//')")

            yield scrapy.FormRequest("https://www.uludagsozluk.com/ax/?a=yenit&ne=ben&nw=pop",
                                     formdata={"benu": l.get_collected_values('user')[0]},
                                     method='POST',
                                     callback=self.parse_post_detail,
                                     dont_filter=True,
                                     meta={'l': l})
            # yield l.load_item()

        next_page_url = response.xpath("//a[@class='nextpage']/@href").extract_first()

        if next_page_url is not None:
            yield scrapy.Request("https://www.uludagsozluk.com" + next_page_url,
                                 callback=self.parse_detail,
                                 dont_filter=True)

    def parse_post_detail(self, response):
        l = response.meta['l']
        user_detail = dict()
        user_detail['bio'] = response.xpath(".//div[@class='popkuladi']/p/small/text()").extract_first()
        for meta in response.xpath("//div[@class='user-stats mhover']/div[@class='stat']"):
            key = str(meta.xpath(".//small/text()").extract_first())
            value = meta.xpath(".//strong/text()").extract_first()
            user_detail[key] = value
        l.add_value("user_detail", user_detail)

        mongo_key = encode_item(dict(l.load_item()))
        ulu_db.update_one({mongo_key: l.load_item()}, {"$set": {mongo_key: l.load_item()}}, upsert=True)

        yield l.load_item()
