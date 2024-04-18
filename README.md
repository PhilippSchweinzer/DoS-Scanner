# dosscanner

This project aims to automate the discovery of denial of service vulnerabilities in web applications. First a crawler gathers information about all links and endpoints on the site which is then used by the scanner to evaluate and test these endpoints for potential attack vectors.


## Installation

1. This project was developed using Python 3.11.2, so make sure you have the correct Python version installed.

2. Install python dependencies.

```bash
pip install -r requirements.txt
```


## Usage

`dosscanner` has two operating modes called `wordlist` and `genetic` which use different principles to find possible attack vectors. They are selected by specifying the mode name as the first parameter to the script. For further help, use the `-h` parameter:

```bash
python dosscanner.py -h
python dosscanner.py wordlist -h
python dosscanner.py genetic -h
```

The following command line arguments can be configured regardless of the chosen mode. Only the `-t TARGET` flag is required.

```
-t TARGET, --target TARGET
                    Target host
-c CRAWL_DEPTH, --crawl-depth CRAWL_DEPTH
                    Maximum crawl depth. (Default: 5)
-r RATE_LIMIT, --rate-limit RATE_LIMIT
                    Rate limit specified in requests per second. (Default: 10000)
-H HEADERS [HEADERS ...], --headers HEADERS [HEADERS ...]
                    Additionaly headers included in every request (Multiple headers: -H "Header1: Value1" "Header2: Value2")
-n, --no-cert-validation
                    Disables certificate validation for requests
-P PROXY, --proxy PROXY
                    Sends every request through the specified proxy
-o OUTPUT, --output OUTPUT
                    Write resulting report into file specified by this path
-v                  Increase output verbosity. Max: -vvv
```

### Wordlist mode

Wordlist mode takes in two different wordlists.
- Parameter name list
  - List containing all parameter names which are of interest to the user. Only parameter names contained in this wordlist are processed by the script. This is done to greatly reduce the number of generated requests and filter unwanted brute force.
- Parameter value list
  - Classic wordlist containing different values which are tested against the target. The original parameter values are substituted by every entry in the list to evaluate the server response time.

These two wordlists combined generate a set of requests which are executed. Their response time is saved and used to calculate the possibility of a denial of service attack on a specific endpoint.

Command line arguments specific to the wordlist mode:


```
usage: dosscanner.py wordlist [-h] -t TARGET -p PARAMS -w WORDLIST [-c CRAWL_DEPTH] [-r RATE_LIMIT] [-H HEADERS [HEADERS ...]] [-n] [-P PROXY] [-o OUTPUT] [-v]

Uses wordlists to create variations of the initial http parameters.

options:
  -h, --help            show this help message and exit

mode specific arguments:
  -p PARAMS, --params PARAMS
                        Path to wordlist specifying names of HTTP GET parameters which are analyzed
  -w WORDLIST, --wordlist WORDLIST
                        Path to wordlist specifying values which are tested on HTTP GET parameters
```

### Genetic mode

Genetic mode uses a genetic algorithm to create mutations of the original parameter values. Mutations are based on a set of operators which are applied to the parameters. Fitness is measured in an improvement of the server response time in respect to the original ancestor. Fitter parts of the population are favored through biased randomness such that a theoretical improvement in response time is achieved over time.

**Warning: This mode requires a large amount of request to work well**

The configuartion of the genetic algorithm can be adjusted using command line arguments specific to genetic mode:

```
dosscanner.py genetic [-h] [-p POPULATION_SIZE] [-e EVOLUTIONS] -t TARGET [-c CRAWL_DEPTH] [-r RATE_LIMIT] [-H HEADERS [HEADERS ...]] [-n] [-P PROXY] [-o OUTPUT] [-v]

Uses a genetic algorithm to create variations of the initial http parameters. This mode requires a large amount of requests to produce the best results.

options:
  -h, --help            show this help message and exit

mode specific arguments:
  -p POPULATION_SIZE, --population-size POPULATION_SIZE
                        Population size used during the genetic evolution. (Default: 20)
  -e EVOLUTIONS, --evolutions EVOLUTIONS
                        Number of evolution cycles the genetic algorithm processes. (Default: 5)
```

## Examples

Example usage of a scan against `https://example.target` using genetic mode, a crawl depth of 7, 10 evolution cycles and maximum verbosity:

```
python dosscanner.py genetic -t https://example.target -c 7 -e 10 -vvv
```

Example usage of a scan against `https://example.target` using wordlist mode, without certificate validation and including a proxy:

```
python dosscanner.py wordlist -t https://example.target -p /path/to/param_list -w /path/to/value_list -n -P "http://127.0.0.1:8080"
```


## Acknowledgements
This project was developed as part of a bachelor thesis under the supervision of Michael Kirchner.
