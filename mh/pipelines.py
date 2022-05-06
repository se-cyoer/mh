# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from re import sub
import redis
import pymongo


class ManhuaPipeline:
    def process_item(self, item, spider):
        return item


class FilterDescribe(object):

    def process_item(self, item, spider):
        dapter = ItemAdapter(item)
        text = str(dapter.get('describe')).strip()
        dapter['describe'] = sub('\n', '', text)
        return item


class SaveRedisPipeline:
    def __init__(self, host, port, indent):
        self.host = host
        self.port = port
        self.indent = indent

    @classmethod
    def from_crawler(cls, crawler):
        host = crawler.settings.get('REDIS_URL', 'localhost')
        port = crawler.settings.get('REDIS_PORT', 6379)
        indent = crawler.settings.get('REDIS_INDENT', 0)
        return cls(host, port, indent)

    def open_spider(self, spider):
        self.db = redis.StrictRedis(host=self.host, port=self.port, db=self.indent, encoding='utf-8')

    def process_item(self, item, spider):
        dict_item = dict(item)
        self.db.rpush('mhdb', dict_item)
        return item

    def close_spider(self, spider):
        self.db.connection_pool.disconnect()


class SaveMongoPipeline:
    def open_spider(self, spider):
        host = spider.settings.get('MONGO_URL', 'localhost')
        port = spider.settings.get('MONGO_PORT', 27017)
        db = spider.settings.get('MONGO_DATABASE', 'mhdb')
        self.client = pymongo.MongoClient(host=host, port=port)
        self.db = self.client[db]
        self.collection = self.db['mh']

    def process_item(self, item, spider):
        self.collection.insert_one(dict(item))
        return item

    def close_spider(self, spider):
        self.client.close()
