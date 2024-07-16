# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json
import os


def clean_text(text):
    # Remove unicode quotation marks
    text = text.replace('\u201c', '').replace('\u201d', '')

    return text


class JsonWriterPipeline(object):

    def open_spider(self, spider):
        self.file = open('quotes_and_authors.json', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        for key, value in item.items():
            if isinstance(value, str):
                item[key] = clean_text(value)

        line = json.dumps(dict(item), indent=4, ensure_ascii=False) + ",\n"
        self.file.write(line)
        return item
