from scrapy.spiders import Spider

from uatube.spiders.items import ManifestChannelItemLoader

TABLE_XPATH = '//tbody[@class="rating-table__body"]'
RANK_XPATH = './/span[@class="rating-item__index"]/span/text()'
CHANNEL_NAME_XPATH = './/a[@class="rating-item__name"]/span/text()'
CHANNEL_URL_XPATH = './/ul[@class="rating-item__btns"]/li[2]/a/@href'
NUM_SUBSCRIBERS_XPATH = '(.//span[@class="rating-item__rating count"])[1]/text()'
NUM_VIEWS_XPATH = '(.//span[@class="rating-item__rating count"])[2]/text()'
NUM_VIDEOS_XPATH = '(.//span[@class="rating-item__rating count"])[3]/text()'
CATEGORIES_XPATH = './/div[@class="rating-item__cats"]/ul/li/a/text()'


class ManifestSpider(Spider):
    name = 'manifest_spider'
    start_urls = ['https://manifest.in.ua/rt/']

    def parse(self, response, **kwargs):
        table = response.xpath(TABLE_XPATH)

        for row in table.xpath(".//tr"):
            loader = ManifestChannelItemLoader(selector=row)
            loader.add_xpath('rank', RANK_XPATH)
            loader.add_xpath('channel_name', CHANNEL_NAME_XPATH)
            loader.add_xpath('channel_id', CHANNEL_URL_XPATH)
            loader.add_xpath('channel_url', CHANNEL_URL_XPATH)
            loader.add_xpath('num_subscribers', NUM_SUBSCRIBERS_XPATH)
            loader.add_xpath('num_views', NUM_VIEWS_XPATH)
            loader.add_xpath('num_videos', NUM_VIDEOS_XPATH)
            loader.add_xpath('categories', CATEGORIES_XPATH)

            yield loader.load_item()
