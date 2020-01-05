import argparse
from elasticsearch import Elasticsearch
import requests
import re
import os
from urllib.parse import urlparse
from datetime import datetime
parser = argparse.ArgumentParser(description='Elastic Search')
parser.add_argument('--update', dest='index', help='index to update'
                    )

parser.add_argument('--ips', dest='ipslist', help='list object to query')
parser.add_argument('--domains', dest='domainslist', help='list object to query')
parser.add_argument('--urls', dest='urlslist', help='list object to query')
args = parser.parse_args()

# print(args.index)

def process_update_ips():
    fetchURL = 'https://raw.githubusercontent.com/stamparm/ipsum/master/ipsum.txt'
    response = requests.get(fetchURL)
    ips = re.findall( r'[0-9]+(?:\.[0-9]+){3}', response.text )
    print("{} ips found".format(len(ips)))
    # just first 100 ips is ok my elastic is to slow..
    ips = ips[0:100]
    # now is time to update elastic we can do it using requests but in this case 
    # we use elasticsearch library
    es = Elasticsearch(
            ["http://{}:9200".format(os.environ['ELASTIC_HOME'])]
    )
    es.indices.delete(index='ips', ignore=[400, 404])
    es.indices.create(index='ips', ignore=400)
    settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "malicious": {
                "properties": {
                    "ip": {
                        "type": "ip"
                    }
                }
            }
         }
    }
    es.index(index="ips", doc_type="ip", body=settings)
    # now ip by ip we ingest data to elastic
    for ip in ips:
        doc = {"ip": ip}
        es.index(index="ips", doc_type="ip", body=doc)

def process_update_urls():
    fetchURL = 'https://urlhaus.abuse.ch/downloads/csv/'

    r = requests.get(fetchURL, stream=True)
    urls = []
    domains = []
    for indx, line in enumerate(r.iter_lines()):
        if indx>8:
            data = line.decode('utf-8')
            url = data.split("\",\"")[2]
            domain = urlparse(url).netloc.split(":")[0]
            urls.append(url)
            domains.append(domain)


    # remove duplicates domains
    domains = list(dict.fromkeys(domains))
    
    # my elastic is to slow with first 100 is ok to test
    domains = domains[0:1000]
    urls = urls[0:1000]

    # we are ready to create index and ingest
    es = Elasticsearch(
            ["http://{}:9200".format(os.environ['ELASTIC_HOME'])]
    )
    es.indices.delete(index='domains', ignore=[400, 404])
    es.indices.create(index='domains', ignore=400)
    settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "malicious": {
                "properties": {
                    "domain": {
                        "type": "keyword"
                    }
                }
            }
         }
    }
    es.index(index="domains",  body=settings)
    # now ip by ip we ingest data to elastic
    for domain in domains:
        doc = {"domain": domain}
        es.index(index="domains", body=doc)

    # FINISHED DOMAINS
    print("Finished domains")
    es.indices.delete(index='urls', ignore=[400, 404])
    es.indices.create(index='urls', ignore=400)
    settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "malicious": {
                "properties": {
                    "url": {
                        "type": "keyword"
                    }
                }
            }
         }
    }
    es.index(index="urls",  body=settings)
    for url in urls:
        doc = {"url": url}
        es.index(index="urls", body=doc)

    print("Finished urls")


def process_update(index):
    validindex = ['ips', 'domains', 'urls', 'hash']
    if index in validindex:
        print("Start processing index: ", index)
        if index=='ips':
            process_update_ips()
        if index=='urls':
            process_update_urls()
        if index=='domains':
            process_update_urls()
        # TODO OTHER INDEX LIKE DOMAINS ETC...
    else:
        raise RuntimeError('invalid index')
   
def process_query_ips(list_args):
    allips = list_args.split(";")
    es = Elasticsearch(
            ["http://{}:9200".format(os.environ['ELASTIC_HOME'])]
    )
    for ip in allips:
        query = {"query":{
                    "match":{
                            "ip": ip                            
                        }    
            }
        }
        result = es.search(index="ips", body=query)
        if int(result['hits']['total']['value']) > 0:
            print("Warning ip {} found".format(ip))

def process_query_domains(list_args):
    alldomains = list_args.split(";")
    es = Elasticsearch(
            ["http://{}:9200".format(os.environ['ELASTIC_HOME'])]
    )
    for domain in alldomains:
        query = {"query":{
                    "match":{
                            "domain": domain
                        }
            }
        }
        result = es.search(index="domains", body=query)
        if int(result['hits']['total']['value']) > 0:
            print("Warning domain {} found".format(domain))

def process_query_urls(list_args):
    allurls = list_args.split(";")
    es = Elasticsearch(
            ["http://{}:9200".format(os.environ['ELASTIC_HOME'])]
    )
    for url in allurls:
        query = {"query":{
                    "match":{
                            "url": url
                        }
            }
        }
        result = es.search(index="urls", body=query)
        if int(result['hits']['total']['value']) > 0:
            print("Warning url {} found".format(url))

def process(args):

    if (args.index):
        process_update(args.index)
    elif (args.ipslist):
        process_query_ips(args.ipslist)
    elif (args.domainslist):
        process_query_domains(args.domainslist)
    elif (args.urlslist):
        process_query_urls(args.urlslist)
    else:
        raise RuntimeError('invalid option')

if __name__ == '__main__':
    process(args)

