import scrapy
from scrapy.exceptions import DropItem

from dosscanner.database import connection
from dosscanner.model import EndpointItem


class EndpointPipeline:
    def process_item(self, item: EndpointItem, spider: scrapy.Spider) -> EndpointItem:
        """Processes item going through crawler pipeline

        Args:
            item (EndpointItem): Item which is passed through the pipeline
            spider (scrapy.Spider): Spider which generated the item

        Raises:
            DropItem: If item is not of type EndpointItem, raise Exception

        Returns:
            EndpointItem: Returns same item which went into the function to be passed into further pipeline calls
        """
        if not isinstance(item, EndpointItem):
            raise DropItem("Item not instance of EndpointItem!")

        with connection:
            connection.execute(
                "INSERT INTO Endpoint ('url', 'http_method') VALUES (?, ?)",
                (item.url, item.http_method),
            )

        return item
