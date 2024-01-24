BOT_NAME = 'uatube'

SPIDER_MODULES = ['uatube.spiders']
NEWSPIDER_MODULE = 'uatube.spiders'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

from scrapy.exporters import JsonItemExporter

from uatube.spiders.items import ManifestChannel


class CustomJsonItemExporter(JsonItemExporter):
    def __init__(self, file, **kwargs):
        super().__init__(file, **kwargs, ensure_ascii=False)


FEED_EXPORTERS = {
    "json": "uatube.scrapysettings.CustomJsonItemExporter"
}

FEEDS = {
    "manifest_top100.json": {
        'format': 'json',
        'encoding': 'utf8',
        'store_empty': False,
        'item_classes': [ManifestChannel],
        'fields': None,
        'indent': 4,
        'item_export_kwargs': {
            'export_empty_fields': True,
        }
    }
}
