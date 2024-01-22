import argparse

from dosscanner import DoSScanner


def cmdline_args():
    # Make parser object
    p = argparse.ArgumentParser(
        prog="main.py", description="Scan web applications for DoS vulnerabilities"
    )

    p.add_argument("--host", dest="host", required=True, help="Target host")

    # Parse arguments
    return p.parse_args()


def main(args):
    scrapy_settings = {
        "ROBOTSTXT_OBEY": True,
        "LOG_LEVEL": "WARNING",
        "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
        "ITEM_PIPELINES": {
            "dosscanner.crawler.pipelines.EndpointPipeline": 0,
        },
    }
    scanner = DoSScanner(target=args.host, scrapy_settings=scrapy_settings)
    print(scanner.scan_target())


if __name__ == "__main__":
    args = cmdline_args()
    main(args)
