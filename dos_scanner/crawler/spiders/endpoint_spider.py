from collections.abc import Iterable
from pathlib import Path
from urllib.parse import urljoin, urlparse
from dos_scanner.crawler.items import EndpointItem
from scrapy.linkextractors import LinkExtractor

import scrapy


class EndpointSpider(scrapy.Spider):
    name = "EndpointSpider"
    max_depth = 2  # Maximum crawl depth
    allowed_domains = []  # To store the domains of the starting URLs
    crawl_subdomains = True
    found_endpoints = set()

    def __init__(self, *args, **kwargs):
        super(EndpointSpider, self).__init__(*args, **kwargs)
        self.allowed_domains.extend(urlparse(start_url).netloc for start_url in self.start_urls)

    def parse(self, response):
        # Stop crawling if maximum depth is reached
        current_depth = response.meta.get('depth', 0)
        if current_depth >= self.max_depth:
            return  
        

        link_ext = LinkExtractor()
        links = link_ext.extract_links(response)

        for link in links:
            yield EndpointItem(url=link.url)

        for link in links:
            yield scrapy.Request(url=link.url, callback=self.parse)



        
        """EndpointItem

        # Extracting all links (endpoints) from the page
        links = response.css('a::attr(href)').getall()


        for link in self.link_extractor.extract_links(response, ):

        absolute_links = [urljoin(response.url, link) for link in links]

        filtered_links = []
        for absolute_link in absolute_links:
            parsed_url = urlparse(absolute_link)
            if self.crawl_subdomains:
                if any(parsed_url.netloc.endswith(domain) for domain in self.allowed_domains):
                    filtered_links.append(absolute_link)
            else:
                if any(parsed_url.netloc == domain for domain in self.allowed_domains):
                    filtered_links.append(absolute_link)

        print('TTTTTTEEEEEEEEEEEEEEESTTTTT', filtered_links)
        self.found_endpoints.update(filtered_links)

        # Follow other links within the website for further scraping
        

        return filtered_links"""
