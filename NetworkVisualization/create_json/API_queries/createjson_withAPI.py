import datetime
import urllib
import json


from wikidataintegrator import wdi_core, wdi_login, wdi_settings
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

    # select  subclasses or instance of item (ie RELN, CRYAB are subclasses of gene)
    prefix = '''
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wikibase: <http://wikiba.se/ontology#>   
    '''

    # for each gene from inner query get list of subclasses
    outer_query = '''
    SELECT DISTINCT ?item WHERE {
    {?item wdt:P31 wd:'''+qid+'''}
    UNION  
    {?item wdt:P279 wd:'''+qid+'''}
    SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }	
    }
    '''
 
    outer_sparql_results = wdi_core.WDItemEngine.execute_sparql_query(prefix=prefix, query=str(outer_query))['results']['bindings']
    
    login_instance = wdi_login.WDLogin(user=wdi_settings.getWikiDataUser(), pwd=wdi_settings.getWikiDataPassword())
    batch_count = 0
    batch_item_count = 0
    batch_item = defaultdict(list)
    # seperate into batches 
    for i in tqdm(outer_sparql_results):
        item = i['item']['value'].split('/')[-1]
        if batch_item_count < 500: # api limit with bot account
            batch_item_count += 1
            batch_item[batch_count].append(item)
        else:
            batch_count += 1
            batch_item_count = 0

    
    prop_value = defaultdict(list)
    prop_ids = list()
    prop_label = list()
    batch_value = list()
    obcount = dict()
    batch_result = tuple()
    # run each specific items in batch via api function
    for i in batch_item: 
        batch_result = wdi_core.WDItemEngine.generate_item_instances(items= batch_item[i], login=login_instance)
        # loop through resulting items list
        for qid, obj in batch_result:
            properties = obj.get_property_list() # get list of properties for this item (specific instance of node)
            result_obj = obj.get_wd_json_representation() # get json object for item
            # for each property get the value qid           
            for k in properties:
                obj_count = 0
                prop_label.append(k) if k not in prop_label else None
                # for each property see if corresponding qid exists 
                for l in result_obj['claims'][k]: # need to add *********COUNT****here too
                    if 'id' in l['mainsnak']['datavalue']['value']:
                        val_qid = l['mainsnak']['datavalue']['value']['id'] # get the value's qid for each property
                        prop_value[k].append(val_qid) if val_qid not in prop_value[k] else None # add this to a hash of the node,property = list of values of property
                        batch_value.append(val_qid) if val_qid not in batch_value else None # add to a overall list to run in batch
                        obj_count += 1
                    else:
                        prop_value[k].append('')
                obcount[k] = obj_count
    
    # run overall list in batch get subclass qids for each qid value
    batch_propqid = defaultdict(list)    
    batch_count = 0
    batch_sc_count = 0
    for i in batch_value:
        if batch_sc_count < 500: # api limit with bot account
            batch_sc_count += 1
            batch_propqid[batch_count].append(i)
        else:
            batch_count += 1
            batch_sc_count = 0

    prop_sc = defaultdict(list)
    batch_sc = list()
    subjcount = dict()
    batch_result = tuple()
    # run each qid in a property
    for i in batch_propqid:
        batch_result = wdi_core.WDItemEngine.generate_item_instances(items= batch_propqid[i], login=login_instance)
        for qid, obj in batch_result:
            result_obj = obj.get_wd_json_representation() # get json object for item
            subj_count = 0
            if 'P279' in result_obj['claims']:
                for k in result_obj['claims']['P279']: # need to *****COUNT**** here
                    if 'id' in k['mainsnak']['datavalue']['value']: 
                        sc_qid = k['mainsnak']['datavalue']['value']['id'] 
                        prop_sc[qid].append(sc_qid) if sc_qid not in prop_sc[qid] else None
                        batch_sc.append(sc_qid) if sc_qid not in batch_sc else None # add to a overall list to run in batch and to get labels
                        subj_count += 1
                subjcount[qid] = subj_count #keyed by qid so need to decode
            if 'P31' in result_obj['claims']:
                for k in result_obj['claims']['P31']: # need to *****COUNT**** here
                    if 'id' in k['mainsnak']['datavalue']['value']: 
                        sc_qid = k['mainsnak']['datavalue']['value']['id'] 
                        prop_sc[qid].append(sc_qid) if sc_qid not in prop_sc[qid] else None
                        batch_sc.append(sc_qid) if sc_qid not in batch_sc else None # add to a overall list to run in batch and to get labels
                        subj_count += 1
                subjcount[qid] = subj_count #keyed by qid so need to decode
    #one more time batch to get the labels

    batch_count = 0
    batch_label_count = 0
    batch_label = defaultdict(list)
    for i in batch_sc:
        if batch_label_count < 500: # api limit with bot account
            batch_label_count += 1
            batch_label[batch_count].append(i)
        else:
            batch_count += 1
            batch_label_count = 0
    for i in prop_label:    
        if batch_label_count < 500: # api limit with bot account
            batch_label_count += 1
            batch_label[batch_count].append(i)
        else:
            batch_count += 1
            batch_label_count = 0

    label = dict()
    batch_result = tuple()
    # run each subclass qid 
    for i in batch_label:
        batch_result = wdi_core.WDItemEngine.generate_item_instances(items= batch_label[i], login=login_instance)
        for qid, obj in batch_result:
            result_obj = obj.get_wd_json_representation()
            if 'value' in result_obj['labels']['en']:
                label[qid] = result_obj['labels']['en']['value']
    # create final dictionary
    d=defaultdict(dict)
    td = defaultdict(dict) #target dictionary
    for i in prop_value:
        for j in prop_value[i]:
            if j == '':
                d[i]['plabel'] = label[i] if i in label else None
            for k in prop_sc[j]:
                d[i]['target'] = dict()
                td[k]['label'] = label[k] if k in label else None
                td[k]['objectcount'] = obcount[i] if i in obcount else None
                td[k]['subjectcount'] = subjcount[k] if k in subjcount else None
                #d[i]['target'][k] = label[k] if k in label else None
                #d[i]['target'][k] = obcount[i] if i in obcount else None
                #d[i]['target'][k] = subjcount[k] if k in subjcount else None
                d[i]['target'][k] = td
                d[i]['direction'] = 'outgoing'
                d[i]['plabel'] = label[i] if i in label else None
     
    

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
    with open('created_api.json','a') as f:  
        json.dump(node,f,indent=4, sort_keys=True) 
        f.close()
    return()   
    
    

#these nodes will eventually be retrieved directly from the url
#node_ids = ['Q7187','Q8054','Q16521','Q12136','Q11173','Q423026', 'Q616005', 'Q898273', 'Q14633912', 'Q417841', 'Q12140', 'Q7644128', 'Q3273544']

node_ids = ['Q12140'] 
#node_ids = ['Q14633912'] # only 4 specifics Q21101039 Q22283748 Q22284210 Q22284208
#properties = node_properties('Q898273') #{'P1057/chromosome/autosome': 13, 'P2293/genetic association/cardiovascular system disease': 1, 'P373/Commons category/': 1}
write_nodes(node_ids)

