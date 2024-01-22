from urllib.parse import urlparse

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from dosscanner.crawler.spiders import EndpointSpider
from dosscanner.database import connection


class DoSScanner:
    def __init__(self, target: str, scrapy_settings: dict = None) -> None:
        self.target = target
        self.scrapy_settings = scrapy_settings

    def scan_target(self) -> list[str]:
        settings = get_project_settings()
        settings.setdict(self.scrapy_settings)

        process = CrawlerProcess(settings)
        process.crawl(
            EndpointSpider,
            allow_domains=[urlparse(self.target).netloc],
            start_urls=[self.target],
        )
        process.start()

        with connection:
            return [
                row[0]
                for row in connection.execute("SELECT url FROM Endpoint").fetchall()
            ]
