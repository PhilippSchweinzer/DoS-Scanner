import scrapy
from scrapy.exceptions import DropItem

from dos_scanner.crawler.items import EndpointItem
from dos_scanner.database import connection


class EndpointPipeline:
    def process_item(self, item: scrapy.Item, spider: scrapy.Spider):
        if not isinstance(item, EndpointItem):
            raise DropItem("Item not instance of EndpointItem!")

        with connection:
            connection.execute(
                "INSERT INTO Endpoint ('url') VALUES (?)", (item["url"],)
            )

        return item
