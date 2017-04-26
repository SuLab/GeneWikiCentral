import datetime
import urllib
import json


from wikidataintegrator import wdi_core, wdi_login, wdi_helpers
from collections import defaultdict
from tqdm import tqdm


class Vividict(dict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value

def node_label(qid):

    prefix = '''
    PREFIX wd: <http://www.wikidata.org/entity/>
    '''

    query = '''
    SELECT DISTINCT * WHERE {
    wd:'''+qid+''' rdfs:label ?label . 
    FILTER (langMatches( lang(?label), "en" ) )  
    }
    limit 1
    '''

    sparql_results = wdi_core.WDItemEngine.execute_sparql_query(prefix=prefix, query=str(query))['results']['bindings']
    label = ''
    for i in sparql_results:
        label = i['label']['value'].split('/')[-1]
    
    return(label)

def node_count(qid):
    
    prefix = '''
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX p: <http://www.wikidata.org/prop/>    
    '''

    query = '''
    SELECT DISTINCT (COUNT(?item) as ?count) WHERE {
    {?item wdt:P31 wd:'''+qid+'''}
    UNION  
    {?item wdt:P279 wd:'''+qid+'''}
    }
    '''

    sparql_results = wdi_core.WDItemEngine.execute_sparql_query(prefix=prefix, query=str(query))['results']['bindings']
    count = ''
    for i in sparql_results:
        count = i['count']['value'].split('/')[-1]
    
    return(count)

def node_properties(qid):
    #dictionary of whether to use instance of or subclass of when querying
    query_spec = {'Q7187':'P279', 'Q8054':'P279','Q16521':'P31','Q12136':'P31','Q11173':'P31','Q423026':'P31', 'Q616005':'P31', 'Q898273':'P31', 'Q14633912':'P279', 'Q417841':'P31', 'Q12140':'P31', 'Q7644128':'P31', 'Q3273544':'P31'}    

    # select  subclasses or instance of item (ie RELN, CRYAB are subclasses of gene) and properties and the subclass for each property
    prefix = '''
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wikibase: <http://wikiba.se/ontology#>   
    '''

    # for each gene from inner query get list of subclasses
    query = '''
    SELECT DISTINCT ?item ?prop ?pLabel ?value ?sc ?scLabel
    WHERE
    {
        ?item wdt:'''+query_spec[qid]+''' wd:'''+qid+'''.
        ?item ?prop ?value .
        ?p wikibase:directClaim ?prop .
        optional {?value wdt:P279 ?sc}
        SERVICE wikibase:label {
            bd:serviceParam wikibase:language "en" .
        }  
        SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }	
    }'''
 
    sparql_results = wdi_core.WDItemEngine.execute_sparql_query(prefix=prefix, query=str(query))['results']['bindings']

    d = defaultdict(dict) # dictionary of all subclasses for each item with a count of times it occurs
    itemuniq = defaultdict(dict)
    #store all the values returned from outer query
    for i in tqdm(sparql_results):
        item = i['item']['value'].split('/')[-1]
        prop = i['prop']['value'].split('/')[-1]
        pLabel = i['pLabel']['value'].split('/')[-1]
        val = i['value']['value'].split('/')[-1]
        sc = ''
        outgoing = ''
        if 'sc' in i:
            sc = i['sc']['value'].split('/')[-1]
            scLabel = i['scLabel']['value'].split('/')[-1]
            outgoing = i['scLabel']['value'].split('/')[-1]
            d[prop]['direction'] = 'outgoing'
        else:
            d[prop]['direction'] = 'outgoing'

        d[prop]['plabel'] = pLabel
        if 'target' in d[prop]: 
            d[prop]['target'].append(outgoing)
        else:
            d[prop]['target'] = list()
            d[prop]['target'].append(outgoing)

        #add counts

            #print(d)
            
        
    return(d)
    

def write_nodes(node_ids):
    i=''
    j=''
    node = defaultdict(list) # contains the list of data which is each node
    edge = defaultdict(list) # contains the list of data for each edge
    # each node check if any other node has the same node label as the the scLabel if so create the edge 
    # loop through     

    for qid in tqdm(node_ids): # this would be each nodes (Qid) data
        nodeattr = defaultdict(dict) # reset for each node as the data makes it not unique
        properties = defaultdict(dict)
        # print(qid)
        properties = node_properties(qid) #get property and counts
        nodeattr['data']['id'] = qid
        nodeattr['data']['label'] = node_label(qid)
        nodeattr['data']['count'] = node_count(qid)
        nodeattr['data']['properties'] = properties
        node['node'].append(nodeattr)

    

        # print(d)
            
    # open json file
    with open('created_sparql.json','a') as f:  
        json.dump(node,f,indent=4, sort_keys=True) 
        f.close()
    return()   
    
#dictionary of whether to use instance of or subclass of when querying
query_spec = {'Q7187':'P279', 'Q8054':'P279','Q16521': 'P31','Q12136':'P31','Q11173':'P31','Q423026':'P31', 'Q616005':'P31', 'Q898273':'P31', 'Q14633912':'P279', 'Q417841':'P31', 'Q12140':'P31', 'Q7644128':'P31', 'Q3273544':'P31'}    

#these nodes will eventually be retrieved directly from the url
#node_ids = ['Q7187','Q8054','Q16521','Q12136','Q11173','Q423026', 'Q616005', 'Q898273', 'Q14633912', 'Q417841', 'Q12140', 'Q7644128', 'Q3273544']

node_ids = ['Q12140']
#node_ids = ['Q14633912'] # only 4 specifics
#properties = node_properties('Q3273544') #{'P1057/chromosome/autosome': 13, 'P2293/genetic association/cardiovascular system disease': 1, 'P373/Commons category/': 1}
write_nodes(node_ids)

