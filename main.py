import argparse

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from dos_scanner.crawler.spiders.endpoint_spider import EndpointSpider
from dos_scanner.database import connection


def cmdline_args():
    # Make parser object
    p = argparse.ArgumentParser(
        prog="main.py", description="Scan web applications for DoS vulnerabilities"
    )

    p.add_argument("--host", dest="host", required=True, help="Target host")

    # Parse arguments
    return p.parse_args()


def main(args):
    settings = get_project_settings()
    settings.setdict(
        {
            "ROBOTSTXT_OBEY": True,
            "LOG_LEVEL": "WARNING",
            "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
            "ITEM_PIPELINES": {
                "dos_scanner.crawler.pipelines.EndpointPipeline": 0,
            },
        }
    )
    process = CrawlerProcess(settings)
    process.crawl(
        EndpointSpider,
        allow_domains=["127.0.0.1:5000"],
        start_urls=["http://127.0.0.1:5000/"],
    )
    process.start()

    with connection:
        print(connection.execute("SELECT * FROM Endpoint").fetchall())


if __name__ == "__main__":
    args = cmdline_args()
    main(args)
