import argparse
from elasticsearch import Elasticsearch
import requests
import re
import os
from datetime import datetime
parser = argparse.ArgumentParser(description='Elastic Search')
parser.add_argument('--update', dest='index', help='index to update'
                    )

parser.add_argument('--ips', dest='ipslist', help='list object to query')
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


def process_update(index):
    validindex = ['ips', 'domains', 'url', 'hash']
    if index in validindex:
        print("Start processing index: ", index)
        if index=='ips':
            process_update_ips()
            print("Finished")
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

def process(args):

    if (args.index):
        process_update(args.index)
    elif (args.ipslist):
        process_query_ips(args.ipslist)
    else:
        raise RuntimeError('invalid option')

if __name__ == '__main__':
    process(args)

