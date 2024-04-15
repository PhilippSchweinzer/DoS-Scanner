import argparse

from dosscanner import DoSScanner, Logger, WordlistMutator, create_report
from dosscanner.mutation.genetic_mutator import GeneticMutator


def cmdline_args():
    # Make parser object
    p = argparse.ArgumentParser(
        prog="main.py", description="Scan web applications for DoS vulnerabilities"
    )

    p.add_argument("--host", dest="host", required=True, help="Target host")
    p.add_argument(
        "-v",
        dest="verbosity_level",
        required=False,
        action="count",
        default=0,
        help="Increase output verbosity. Max: -vvv",
    )
    p.add_argument(
        "--crawl-depth",
        dest="crawl_depth",
        required=False,
        type=int,
        default=3,
        help="Maximum crawl depth",
    )
    p.add_argument(
        "-o",
        "--output",
        dest="output",
        required=False,
        help="Path to write resulting report into file",
    )

    # Parse arguments
    return p.parse_args()


def main(args):
    Logger.verbosity_level = args.verbosity_level

    mutator = GeneticMutator(population_size=20, max_evolutions=6)

    # mutator = WordlistMutator(
    #    "/home/philipp/Desktop/git_repos/DoS-Scanner/dataset.txt",
    #    "/home/philipp/Desktop/git_repos/DoS-Scanner/params.txt",
    # )
    scanner = DoSScanner(target=args.host, mutator=mutator)
    vulnerable_endpoints, all_endpoints = scanner.scan_target()

    report = create_report(vulnerable_endpoints, all_endpoints)
    if args.output is not None:
        with open(args.output, "w") as f:
            f.write(report)
    print(report)


if __name__ == "__main__":
    args = cmdline_args()
    main(args)
