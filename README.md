# minithreadINTEL

CyberSec Intel with Elastic

# Requirement

- VirtualEnv
- Python3.7

#Installation

- source venv/bin/activate
- pip install -r requirement.txt

# Usage

## Update IP

python elastic.py -u ips

## Update domains

python elastic.py -u domains

## Update URL

python elastic.py -u urls

## Update Hash

python elastic.py -u hash

## query based

-q [index_name][list coma separated]

python elastic.py -q ips 1.1.1.1;123.123.123.123;
