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

def node_count(qid): # could count as go through items to save time
    # dictionary of whether to use instance of or subclass of when querying
    query_spec = {'Q7187':'P279', 'Q8054':'P279','Q16521': 'P31','Q12136':'P31','Q11173':'P31','Q423026':'P31', 'Q616005':'P31', 'Q898273':'P31', 'Q14633912':'P279', 'Q417841':'P31', 'Q12140':'P31', 'Q7644128':'P31', 'Q3273544':'P31'} 
    prefix = '''
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX p: <http://www.wikidata.org/prop/>    
    '''

    query = '''
    SELECT DISTINCT (COUNT(?item) as ?count) WHERE {
        ?item wdt:'''+query_spec[qid]+''' wd:'''+qid+'''
    }
    '''

    sparql_results = wdi_core.WDItemEngine.execute_sparql_query(prefix=prefix, query=str(query))['results']['bindings']
    count = ''
    for i in sparql_results:
        count = i['count']['value'].split('/')[-1]
    
    return(count)

def node_properties(qid):
    # dictionary of whether to use instance of or subclass of when querying
    query_spec = {'Q7187':'P279', 'Q8054':'P279','Q16521': 'P31','Q12136':'P31','Q11173':'P31','Q423026':'P31', 'Q616005':'P31', 'Q898273':'P31', 'Q14633912':'P279', 'Q417841':'P31', 'Q12140':'P31', 'Q7644128':'P31', 'Q3273544':'P31'} 

    # select  subclasses or instance of item (ie RELN, CRYAB are subclasses of gene)
    prefix = '''
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wikibase: <http://wikiba.se/ontology#>   
    '''

    # for each gene from inner query get list of subclasses
    outer_query = '''
    SELECT DISTINCT ?item WHERE {
        ?item wdt:'''+query_spec[qid]+''' wd:'''+qid+'''	
    }
    '''
 
    outer_sparql_results = wdi_core.WDItemEngine.execute_sparql_query(prefix=prefix, query=str(outer_query))['results']['bindings']

    # loop through each item in outer query and add counts to global counts
    d = defaultdict(dict) # dictionary of all properties for each node
    # make a dictionary of each property and do counts
    scount = defaultdict(dict) # holds counts for this item only
    ocount = defaultdict(dict) # holds counts for this item only
    labels = dict()
    for i in tqdm(outer_sparql_results):
        item = i['item']['value'].split('/')[-1]

        # get list of specific things (in case of gene specific type ie RELN)
        inner_query = '''
        SELECT ?prop ?pLabel ?value ?sc ?scLabel WHERE {
        wd:'''+item+''' ?prop ?value .
        ?p wikibase:directClaim ?prop .
        optional {?value wdt:P279 ?sc}
        SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }  
        }
        '''       
 
        inner_sparql_results = wdi_core.WDItemEngine.execute_sparql_query(prefix=prefix, query=str(inner_query))['results']['bindings']

        
        for j in inner_sparql_results:
            prop = j['prop']['value'].split('/')[-1]
            pLabel = j['pLabel']['value'].split('/')[-1]
            propval = j['value']['value'].split('/')[-1]
            sc = ''
            scLabel = ''
            outgoing = ''
            d[prop]['target'] = defaultdict(list)
            if 'sc' in j: 
                sc = j['sc']['value'].split('/')[-1]
                scLabel = j['scLabel']['value'].split('/')[-1]
                if sc in ocount[prop]:
                    ocount[prop][sc] += 1
                else:
                    ocount[prop][sc] = 1
                    scount[prop][sc] = dict()
                #print(ocount)
                
                if propval in scount[prop][sc]:
                    scount[prop][sc][propval] += 1
                else:            
                   scount[prop][sc][propval] = 1         
                #print(scount)             

            else: # sometimes there isn't a subclass ie GO terms 
                d[prop]['objectcount'] = 0
                if 'subjectcount' in d[prop]:
                    d[prop]['subjectcount']  += 1
                else:
                    d[prop]['subjectcount'] = 1
                    
            d[prop]['pLabel'] = pLabel
            d[prop]['direction'] = 'outgoing'
            labels[sc] = scLabel

        for propk in ocount:
            d[propk]['target']= list()
            for sck in ocount[propk]:
                temp = dict()
                temp['subjectcount'] = 0
                temp['id'] = sck
                temp['label'] = labels[sck]
                temp['objectcount'] = ocount[propk][sck]
                for vk in scount[propk][sck]:
                    temp['subjectcount'] += scount[propk][sck][vk]
                d[propk]['target'].append(temp)
  
            
        
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
    
   
    

#these nodes will eventually be retrieved directly from the url
#node_ids = ['Q7187','Q8054','Q16521','Q12136','Q11173','Q423026', 'Q616005', 'Q898273', 'Q14633912', 'Q417841', 'Q12140', 'Q7644128', 'Q3273544']

#node_ids = ['Q12140']
node_ids = ['Q14633912'] # only 4 specifics
#properties = node_properties('Q3273544') #{'P1057/chromosome/autosome': 13, 'P2293/genetic association/cardiovascular system disease': 1, 'P373/Commons category/': 1}
write_nodes(node_ids)

