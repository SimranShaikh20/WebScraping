# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class FreshersworldPipeline:
    def process_item(self, item, spider):
        return item
import json

class JsonWriterPipeline:
    def __init__(self):
        self.file = open('data.json', 'w')

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item

    def close_spider(self, spider):
        self.file.close()