# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from dos_scanner.crawler.items import EndpointItem
from scrapy.exceptions import DropItem
from itemadapter import ItemAdapter
from dos_scanner.database import connection

class EndpointPipeline:
    def process_item(self, item: scrapy.Item, spider: scrapy.Spider):
        if not isinstance(item, EndpointItem):
            raise DropItem("Item not instance of EndpointItem!")
        
        with connection:
            connection.execute("INSERT INTO Endpoint ('url') VALUES (?)", (item['url'],))
            
        return item
