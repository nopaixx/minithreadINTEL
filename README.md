# minithreadINTEL

CyberSec Intel with Elastic

# Requirement

- VirtualEnv
- Python3.7

# Installation

update you elastic home in envvars files

- source venv/bin/activate
- source envvars
- pip install -r requirement.txt

# Usage

## Update IP

python elastic.py --update ips

![example](https://github.com/nopaixx/minithreadINTEL/blob/master/demo2.png)

## Update domains

python elastic.py -update domains

## Update URL

python elastic.py -update urls

## Update Hash

python elastic.py -update hash

## query based

python elastic.py --INDEX_NAME [list coma separated]

python elastic.py --ips "1.1.1.1;123.123.123.123;104.244.79.181;69.158.207.141"

![example](https://github.com/nopaixx/minithreadINTEL/blob/master/demo1.png)

python elastic.py --domains "pastebin.com;google.com"

![example](https://github.com/nopaixx/minithreadINTEL/blob/master/demo3.png)
