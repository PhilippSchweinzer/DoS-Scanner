import argparse

from dosscanner import DoSScanner, Logger, Requestor, WordlistMutator, create_report
from dosscanner.logger import LogLevel
from dosscanner.model import Endpoint
from dosscanner.mutation.genetic_mutator import GeneticMutator


def cmdline_args():
    # Parent parser
    parser = argparse.ArgumentParser(
        prog="dosscanner.py",
        description="Scan a target web server to find potential denial of service vulnerabilities.",
        epilog="This project was developed by Philipp Schweinzer as part of a bachelor thesis under the supervision of Michael Kirchner.",
    )

    # Subparsers for different modes of operation
    subparsers = parser.add_subparsers(
        help="Mode of operation used during detection of denial of service vulnerabilities",
        required=True,
        dest="mode",
    )
    genetic_parser = subparsers.add_parser(
        "genetic",
        description="Uses a genetic algorithm to create variations of the initial http parameters. This mode requires a large amount of requests to produce the best results.",
    )
    wordlist_parser = subparsers.add_parser(
        "wordlist",
        description="Uses wordlists to create variations of the initial http parameters.",
    )

    # Argument groups for better visualization
    specific_args_genetic = genetic_parser.add_argument_group("mode specific arguments")
    specific_args_wordlist = wordlist_parser.add_argument_group(
        "mode specific arguments"
    )
    general_args_genetic = genetic_parser.add_argument_group("general arguments")
    general_args_wordlist = wordlist_parser.add_argument_group("general arguments")

    # Arguments of genetic subparser
    specific_args_genetic.add_argument(
        "-p",
        "--population-size",
        dest="population_size",
        required=False,
        type=int,
        default=20,
        help="Population size used during the genetic evolution. (Default: %(default)d)",
    )
    specific_args_genetic.add_argument(
        "-e",
        "--evolutions",
        dest="evolutions",
        required=False,
        type=int,
        default=5,
        help="Number of evolution cycles the genetic algorithm processes. (Default: %(default)d)",
    )

    general_args_genetic.add_argument(
        "-t", "--target", dest="target", required=True, help="Target host"
    )
    general_args_genetic.add_argument(
        "-c",
        "--crawl-depth",
        dest="crawl_depth",
        required=False,
        type=int,
        default=5,
        help="Maximum crawl depth. (Default: %(default)d)",
    )
    general_args_genetic.add_argument(
        "-r",
        "--rate-limit",
        dest="rate_limit",
        required=False,
        type=int,
        default=200,
        help="Rate limit specified in requests per second. (Default: %(default)d)",
    )
    general_args_genetic.add_argument(
        "-H",
        "--headers",
        dest="headers",
        nargs="+",
        required=False,
        help='Additionaly headers included in every request (Multiple headers: -H "Header1: Value1" "Header2: Value2")',
    )
    general_args_genetic.add_argument(
        "-n",
        "--no-cert-validation",
        dest="no_cert_validation",
        action="store_true",
        required=False,
        help="Disables certificate validation for requests",
    )
    general_args_genetic.add_argument(
        "-P",
        "--proxy",
        dest="proxy",
        required=False,
        help="Sends every request through the specified proxy",
    )
    general_args_genetic.add_argument(
        "-o",
        "--output",
        dest="output",
        required=False,
        help="Write resulting report into file specified by this path",
    )
    general_args_genetic.add_argument(
        "-v",
        dest="verbosity_level",
        required=False,
        action="count",
        default=0,
        help="Increase output verbosity. Max: -vvv",
    )

    # Arguments of wordlist subparser
    general_args_wordlist.add_argument(
        "-t", "--target", dest="target", required=True, help="Target host"
    )
    specific_args_wordlist.add_argument(
        "-p",
        "--params",
        dest="params",
        required=True,
        help="Path to wordlist specifying names of HTTP GET parameters which are analyzed",
    )
    specific_args_wordlist.add_argument(
        "-w",
        "--wordlist",
        dest="wordlist",
        required=True,
        help="Path to wordlist specifying values which are tested on HTTP GET parameters",
    )
    general_args_wordlist.add_argument(
        "-c",
        "--crawl-depth",
        dest="crawl_depth",
        required=False,
        type=int,
        default=5,
        help="Maximum crawl depth. (Default: %(default)d)",
    )
    general_args_wordlist.add_argument(
        "-r",
        "--rate-limit",
        dest="rate_limit",
        required=False,
        type=int,
        default=200,
        help="Rate limit specified in requests per second. (Default: %(default)d)",
    )
    general_args_wordlist.add_argument(
        "-H",
        "--headers",
        dest="headers",
        nargs="+",
        required=False,
        help='Additionaly headers included in every request (Multiple headers: -H "Header1: Value1" "Header2: Value2")',
    )
    general_args_wordlist.add_argument(
        "-n",
        "--no-cert-validation",
        dest="no_cert_validation",
        action="store_true",
        required=False,
        help="Disables certificate validation for requests",
    )
    general_args_wordlist.add_argument(
        "-P",
        "--proxy",
        dest="proxy",
        required=False,
        help="Sends every request through the specified proxy",
    )
    general_args_wordlist.add_argument(
        "-o",
        "--output",
        dest="output",
        required=False,
        help="Write resulting report into file specified by this path",
    )
    general_args_wordlist.add_argument(
        "-v",
        dest="verbosity_level",
        required=False,
        action="count",
        default=0,
        help="Increase output verbosity. Max: -vvv",
    )

    # Parse arguments
    return parser.parse_args()


def main(args):

    # Set logging verbosity level
    Logger.verbosity_level = args.verbosity_level

    # Set header values of Requestor
    if args.headers is not None:
        for header in args.headers:
            key, value = header.split(": ", maxsplit=1)
            Requestor.headers[key] = value

    # Set flag for certificate validation
    if args.no_cert_validation:
        Requestor.certificate_validation = False

    # Set proxy settings of Requestor
    if args.proxy is not None:
        Requestor.proxies["http"] = args.proxy
        Requestor.proxies["https"] = args.proxy

    # Create specified mutator from command line args
    if args.mode == "genetic":
        Logger.trace("Using genetic mode")
        mutator = GeneticMutator(
            population_size=args.population_size, max_evolutions=args.evolutions
        )
    elif args.mode == "wordlist":
        Logger.trace("Using wordlist mode")
        mutator = WordlistMutator(args.wordlist, args.params)

    success, message = Requestor.check_connectivity(
        Endpoint(url=args.target, http_method="GET")
    )
    if not success:
        Logger.error(f"Connectivity test to target server failed! Error: {message}")
        return
    else:
        Logger.trace("Connectivity test to target server succeeded!")

    # Create scanner and start it
    scanner = DoSScanner(
        target=args.target, mutator=mutator, crawl_depth=args.crawl_depth
    )
    vulnerable_endpoints, all_endpoints = scanner.scan_target()

    # Create report from list of endpoints given by the scanner
    Logger.trace("Creating report")
    report = create_report(vulnerable_endpoints, all_endpoints)
    if args.output is not None:
        with open(args.output, "w") as f:
            f.write(report)
    else:
        print(report)


if __name__ == "__main__":
    args = cmdline_args()
    main(args)
