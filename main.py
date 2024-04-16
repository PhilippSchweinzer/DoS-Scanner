import argparse

from dosscanner import DoSScanner, Logger, WordlistMutator, create_report
from dosscanner.mutation.genetic_mutator import GeneticMutator


def cmdline_args():
    # Parent parser
    parser = argparse.ArgumentParser(
        prog="main.py", description="Scan web applications for DoS vulnerabilities"
    )

    # Subparsers for different modes of operation
    subparsers = parser.add_subparsers(
        help="Mode of operation used during Denial of Service evaluation",
        required=True,
        dest="mode",
    )
    genetic_parser = subparsers.add_parser("genetic")
    wordlist_parser = subparsers.add_parser("wordlist")

    # Arguments of genetic subparser
    genetic_parser.add_argument(
        "--host", dest="host", required=True, help="Target host"
    )
    genetic_parser.add_argument(
        "-p",
        "--population-size",
        dest="population_size",
        required=False,
        default=20,
        help="Population size used during the genetic evolution",
    )
    genetic_parser.add_argument(
        "-e",
        "--evolutions",
        dest="evolutions",
        required=False,
        default=5,
        help="Number of evolutions the genetic algorithm processes",
    )
    genetic_parser.add_argument(
        "-v",
        dest="verbosity_level",
        required=False,
        action="count",
        default=0,
        help="Increase output verbosity. Max: -vvv",
    )
    genetic_parser.add_argument(
        "-c",
        "--crawl-depth",
        dest="crawl_depth",
        required=False,
        type=int,
        default=5,
        help="Maximum crawl depth",
    )
    genetic_parser.add_argument(
        "-o",
        "--output",
        dest="output",
        required=False,
        help="Path to write resulting report into file",
    )

    # Arguments of wordlist subparser
    wordlist_parser.add_argument(
        "--host", dest="host", required=True, help="Target host"
    )
    wordlist_parser.add_argument(
        "--wordlist", dest="wordlist", required=True, help="Path to wordlist"
    )
    wordlist_parser.add_argument(
        "--paramlist", dest="paramlist", required=True, help="Path to paramlist"
    )
    wordlist_parser.add_argument(
        "-v",
        dest="verbosity_level",
        required=False,
        action="count",
        default=0,
        help="Increase output verbosity. Max: -vvv",
    )
    wordlist_parser.add_argument(
        "-c",
        "--crawl-depth",
        dest="crawl_depth",
        required=False,
        type=int,
        default=3,
        help="Maximum crawl depth",
    )
    wordlist_parser.add_argument(
        "-o",
        "--output",
        dest="output",
        required=False,
        help="Path to write resulting report into file",
    )

    # Parse arguments
    return parser.parse_args()


def main(args):

    # Set logging verbosity level
    Logger.verbosity_level = args.verbosity_level

    # Create specified mutator from command line args
    if args.mode == "genetic":
        mutator = GeneticMutator(
            population_size=args.population_size, max_evolutions=args.evolutions
        )
    elif args.mode == "wordlist":
        mutator = WordlistMutator(args.wordlist, args.paramlist)

    # Create scanner and start it
    scanner = DoSScanner(target=args.host, mutator=mutator)
    vulnerable_endpoints, all_endpoints = scanner.scan_target()

    # Create report from list of endpoints given by the scanner
    report = create_report(vulnerable_endpoints, all_endpoints)
    if args.output is not None:
        with open(args.output, "w") as f:
            f.write(report)
    print(report)


if __name__ == "__main__":
    args = cmdline_args()
    main(args)
