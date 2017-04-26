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
    #query_spec = {'Q7187':'P279', 'Q8054':'P279','Q16521': 'P31','Q12136':'P31','Q11173':'P31','Q423026':'P31', 'Q616005':'P31', 'Q898273':'P31', 'Q14633912':'P279', 'Q417841':'P31', 'Q12140':'P31', 'Q7644128':'P31', 'Q3273544':'P31'} 
    query_spec = {'Q7187':'P279', 'Q8054':'P279','Q16521': 'P31','Q12136':'P31','Q11173':'P31','Q423026':'P31', 'Q616005':'P31', 'Q898273':'P31', 'Q14633912':'P279', 'Q417841':'P31', 'Q12140':'P31', 'Q7644128':'P31', 'Q3273544':'P31', 'Q14863042': 1, 'Q14633914': 1} 

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
    e = list()  #save edges if one of list of nodes
    edge_count = dict()
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
            
            if 'sc' in j:
                sc = j['sc']['value'].split('/')[-1]
                scLabel = j['scLabel']['value'].split('/')[-1]
                
            d[prop]['pLabel'] = pLabel
            d[prop]['direction'] = 'outgoing'
            #labels[sc] = scLabel
            if sc != '':
                if 'target' in d[prop]:
                    d[prop]['target'][sc] = scLabel
                else:
                    d[prop]['target'] = dict()
                    d[prop]['target'][sc] = scLabel
            edgeattr = defaultdict(dict) # create list of attributes
            if sc in query_spec:
                edgeattr['data']['id'] = qid + "'" + sc
                edgeattr['data']['enname'] =  node_label(qid) + "'" + scLabel
                edgeattr['data']['source'] = qid
                edgeattr['data']['target'] = sc
                edgeattr['data']['label'] = pLabel
                edgeattr['data']['propid'] = prop
                edgeattr['data']['count'] = ''
                edgeattr['data']['qualifier'] = ''
                edgeattr['data']['refprop'] = ''
                if prop in edge_count:
                    edge_count[prop] = edge_count[prop] + 1
                else:
                    edge_count[prop] = 1
                    #e['edges'].append(edgeattr)
                    e.append(edgeattr)
        
             
    return(d, e)
    

def write_nodes(node_ids):
    i=''
    j=''
    nodedge = defaultdict(list) # contains the list of data which is each node and egde
    # each node check if any other node has the same node label as the the scLabel if so create the edge 
    # loop through     

    for qid in tqdm(node_ids): # this would be each nodes (Qid) data
        nodeattr = defaultdict(dict) # reset for each node as the data makes it not unique
        properties = defaultdict(dict)
        # print(qid)
        properties, edgeattr = node_properties(qid) #get property

        nodeattr['data']['id'] = qid
        nodeattr['data']['label'] = node_label(qid)
        nodeattr['data']['count'] = node_count(qid)
        nodeattr['data']['properties'] = properties
        nodedge['nodes'].append(nodeattr)
        nodedge['edges'].append(edgeattr) #this isn't quite right there are extra brackets so it doesn't display correctly in cytoscape

        # print(d)
            
    # open json file
    with open('test.json','a') as f:  
        json.dump(nodedge,f,indent=4, sort_keys=True)
    f.close()
    return()   
    
   
    

#these nodes will eventually be retrieved directly from the url
#node_ids = ['Q7187','Q8054','Q16521','Q12136','Q11173','Q423026', 'Q616005', 'Q898273', 'Q14633912', 'Q417841', 'Q12140', 'Q7644128', 'Q3273544']

#node_ids = ['Q12140']
node_ids = ['Q14633912','Q616005'] # only 4 specifics, 175, 286 ,'Q3273544'
#properties = node_properties('Q3273544') #{'P1057/chromosome/autosome': 13, 'P2293/genetic association/cardiovascular system disease': 1, 'P373/Commons category/': 1}
write_nodes(node_ids)

