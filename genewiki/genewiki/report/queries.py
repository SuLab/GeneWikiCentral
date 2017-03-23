from django.db import connections

from wikidataintegrator import wdi_core, wdi_login, wdi_helpers
import datetime
import urllib

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


# counts based on jenkins runs
def gene_counts(kingdom):
    cursor = connections['mysql_amazon'].cursor()
    query = "SELECT DISTINCT g.wd_tax_label as species, g.kingdom as kingdom,  g.class as class, DATE(c.date) as date, c.counts FROM  semtype_counts AS c JOIN genes AS g  ON g.sem_type_id = c.semtype_id;"
    cursor.execute(query)
    pre_dict = dictfetchall(cursor)
    # reformat results for output ie keyed by date then kingdom then species
    results = dict()

    for row in pre_dict:
        date = row['date'].strftime('%Y-%m-%d')
        if results.get(date) is None:
            results[date] = {}
        if kingdom == 'bacteria':    # combine count per class for bacteria
            if row['kingdom'] == kingdom:
                if date in results:
                    if row['class'] in results[date]:
                        results[date][row['class']] = results[date][row['class']] + row['counts']
                    else:
                        results[date][row['class']] = row['counts']
        else:  # if not bacteria then split up by species
            if row['kingdom'] != 'bacteria':
                if date in results:
                    if row['species'] == 'house mouse':
                        row['species'] = 'Mus musculus'
                    results[date][row['species']] = row['counts']

    return results


def disease_counts():
    cursor = connections['mysql_amazon'].cursor()
    query ="SELECT DISTINCT DATE(c.date) as date, c.counts, st.genewiki_sem_type_label as label FROM wikidata_logs.semtype_counts AS c JOIN sem_types AS st ON c.semtype_id = st.wd_id WHERE main_type = 'disease';"
    cursor.execute(query)
    pre_dict = dictfetchall(cursor)
    #format results keyed by date then my ontology source
    results = dict()

    for row in pre_dict:
        date = row['date'].strftime('%Y-%m-%d')
        if results.get(date) is None:
            results[date] = {}
        if date in results:
            results[date][row['label']] = row['counts']
    
    return results

def bot_update(bot):
    cursor = connections['mysql_amazon'].cursor()
    query = "SELECT COUNT(*) as count, update_date, update_type  FROM wikidata_logs.update_history WHERE main_type = '%s' AND update_type IS NOT NULL GROUP BY update_type;" % bot
    cursor.execute(query)
    # results = dictfetchall(cursor)
    results = [{'count': 1,'update_date': '10-02-2016','update_type': 'created' },{'count': 2,'update_date': '10-03-2016','update_type': 'merged'},{'count': 4,'update_date': '10-02-2016','update_type': 'updated'}]
    return results

def get_errors():
    cursor = connections['mysql_amazon'].cursor()
    query ="SELECT jenkins_bot_task as bot, error_class, error_message, DATE(error_timestamp) as date, qid FROM wikidata_logs.PBB_Core_ERRORS;"
    cursor.execute(query)
    # maybe date will need some formatting
    # results = dictfetchall(cursor)
    results = [{'bot': 'gene', 'error_class': 'null value', 'error_message':'value not found in line...', 'date': '8-10-2016', 'qid': 'Q123940'}, {'bot': 'gene', 'error_class': 'data type', 'error_message':'mismatch datatype...', 'date': '8-10-2016', 'qid': 'Q1283748'}, {'bot': 'gene', 'error_class': 'key error', 'error_message':'key value occurred...', 'date': '8-16-2016', 'qid': 'Q1294472'}]
    return results


def get_error_month():
    # Only displaying 1 months worth of errors
    cursor = connections['mysql_amazon'].cursor()
    query ="SELECT jenkins_bot_task, error_class, error_message, DATE(error_timestamp) as date, qid FROM wikidata_logs.PBB_Core_ERRORS where error_timestamp BETWEEN NOW() - INTERVAL 30 DAY AND NOW();"
    cursor.execute(query)
    # results = dictfetchall(cursor)
    results = [{'bot': 'gene', 'error_class': 'null value', 'error_message':'value not found in line...', 'date': '8-10-2016', 'qid': 'Q123940'}, {'bot': 'gene', 'error_class': 'data type', 'error_message':'mismatch datatype...', 'date': '8-10-2016', 'qid': 'Q1283748'}, {'bot': 'gene', 'error_class': 'key error', 'error_message':'key value occurred...', 'date': '8-16-2016', 'qid': 'Q1294472'}]
    return results
    

# counts based on current wikidata
def get_genes():
    # get the list of model organims counting proteins for
    cursor = connections['mysql_amazon'].cursor()
    query = "SELECT DISTINCT g.sem_type_id FROM  semtype_counts AS c JOIN genes AS g  ON g.sem_type_id = c.semtype_id where kingdom <> 'bacteria';"
    cursor.execute(query)
    results = dictfetchall(cursor)
    qids_model_organism = ''
    for row in results:
       qids_model_organism += 'wd:'+str(row['sem_type_id'])+' '
        
    # Query wikidata to get the number of human genes
    prefix = '''
    PREFIX wd: <http://www.wikidata.org/entity/> 
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    '''

    query = '''
    SELECT DISTINCT (count(?gene) as ?no_genes)
    WHERE 
    { 
        VALUES ?organism { %s }
        ?gene wdt:P279 wd:Q7187 .
        ?gene wdt:P703 ?organism.
        OPTIONAL{?gene rdfs:label ?gene_label filter (lang(?gene_label)="en").} 
    }
    ''' % qids_model_organism

    sparql_results = wdi_core.WDItemEngine.execute_sparql_query(prefix=prefix, query=query)['results']['bindings']
    count = ''
    for i in sparql_results:
        count = i['no_genes']['value'].split('/')[-1]

    joined_query = prefix+query
    url_query = 'https://query.wikidata.org/#'+urllib.parse.quote(joined_query)
    url_link = '<a href="'+url_query+'">click to execute gene query</a>'

    return(count, url_link)


def get_proteins():
    # get the list of model organims counting proteins for
    cursor = connections['mysql_amazon'].cursor()
    query = "SELECT DISTINCT g.sem_type_id FROM  semtype_counts AS c JOIN genes AS g  ON g.sem_type_id = c.semtype_id where kingdom <> 'bacteria';"
    cursor.execute(query)
    results = dictfetchall(cursor)
    qids_model_organism = ''
    for row in results:
       qids_model_organism += 'wd:'+str(row['sem_type_id'])+' '

    # Query wikidata to get the number of human proteins
    prefix = '''
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    '''

    query = '''
    SELECT DISTINCT (count(?protein) as ?no_proteins)
    WHERE 
    { 
        VALUES ?organism { %s }
        ?protein wdt:P279 wd:Q8054 . 
        ?protein wdt:P703 ?organism.
        OPTIONAL{?protein rdfs:label ?protein_label filter (lang(?protein_label)="en").} 
    }
    ''' % qids_model_organism

    sparql_results = wdi_core.WDItemEngine.execute_sparql_query(prefix=prefix, query=query)['results']['bindings']
    count = ''
    for i in sparql_results:
        count = i['no_proteins']['value'].split('/')[-1]

    joined_query = prefix+query
    url_query = 'https://query.wikidata.org/#'+urllib.parse.quote(joined_query)
    url_link = '<a href="'+url_query+'">click to execute protein query</a>'

    return(count, url_link)


def get_diseases():
    # Query wikidata to get the number of disease ontology terms
    prefix = '''
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX p: <http://www.wikidata.org/prop/>
    PREFIX wikibase: <http://wikiba.se/ontology#>
    '''

    query = '''
    SELECT DISTINCT (COUNT(?diseases) as ?count)  WHERE {
    ?diseases p:P699 ?doid .
    ?doid wikibase:rank ?rank .
    }
    '''
    sparql_results = wdi_core.WDItemEngine.execute_sparql_query(prefix=prefix, query=query)['results']['bindings']
    count = ''
    for i in sparql_results:
        count = i['count']['value'].split('/')[-1]

    joined_query = prefix+query
    url_query = 'https://query.wikidata.org/#'+urllib.parse.quote(joined_query)
    url_link = '<a href="'+url_query+'">click to execute disease query</a>'

    return(count, url_link)


def get_compounds():
    # Query wikidata to get the number of compounds (drugs)
    prefix = '''
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX p: <http://www.wikidata.org/prop/>
    PREFIX v: <http://www.wikidata.org/prop/statement/>
    '''

    query = '''
    SELECT (COUNT (DISTINCT ?chembl) AS ?count)  WHERE {
    ?compound wdt:P592 ?chembl .
    OPTIONAL  {?compound rdfs:label ?label filter (lang(?label) = "en")}
    }
    '''
    sparql_results = wdi_core.WDItemEngine.execute_sparql_query(prefix=prefix, query=query)['results']['bindings']
    count = ''
    for i in sparql_results:
        count = i['count']['value'].split('/')[-1]

    joined_query = prefix+query
    url_query = 'https://query.wikidata.org/#'+urllib.parse.quote(joined_query)
    url_link = '<a href="'+url_query+'">click to execute compound query</a>'

    return(count, url_link)


def get_mspecies():
    # Query wikidata to get the number of microbial species
    prefix = '''
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    '''

    query = '''
    SELECT   (COUNT (DISTINCT ?species) AS ?count)  WHERE {
    ?gene wdt:P351 ?entrezID . # P351 Entrez Gene ID
    ?gene wdt:P703 ?species . # P703 Found in taxon
    ?species wdt:P171* wd:Q10876 .
    ?species rdfs:label ?label filter (lang(?label) = "en") .
    }
    '''
    sparql_results = wdi_core.WDItemEngine.execute_sparql_query(prefix=prefix, query=query)['results']['bindings']
    count = ''
    for i in sparql_results:
        count = i['count']['value'].split('/')[-1]
    return(count)


def get_mgenes():
    # Query wikidata to get the number of microbial genes
    prefix = '''
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    '''

    query = '''
    SELECT (COUNT (DISTINCT ?gene) AS ?count)  WHERE {
    ?gene wdt:P351 ?entrezID . # P351 Entrez Gene ID
    ?gene wdt:P703 ?species . # P703 Found in taxon
    ?species wdt:P171* wd:Q10876 .
    ?species rdfs:label ?label filter (lang(?label) = "en") .
    }
    '''
    sparql_results = wdi_core.WDItemEngine.execute_sparql_query(prefix=prefix, query=query)['results']['bindings']
    count = ''
    for i in sparql_results:
        count = i['count']['value'].split('/')[-1]

    joined_query = prefix+query
    url_query = 'https://query.wikidata.org/#'+urllib.parse.quote(joined_query)
    url_link = '<a href="'+url_query+'">click to execute microbial gene query</a>'

    return(count, url_link)


def get_mproteins():
    # Query wikidata to get the number of microbial proteins
    prefix = '''
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    '''

    query = '''
    SELECT (COUNT (DISTINCT ?protein) AS ?count)  WHERE {
    ?protein wdt:P352 ?uniprotID . # P352 UniProt ID
    ?protein wdt:P703 ?species . # P703 Found in taxon
    ?species wdt:P171* wd:Q10876 .
    ?species rdfs:label ?label filter (lang(?label) = "en") .
    }
    '''
    sparql_results = wdi_core.WDItemEngine.execute_sparql_query(prefix=prefix, query=query)['results']['bindings']
    count = ''
    for i in sparql_results:
        count = i['count']['value'].split('/')[-1]
    return(count)
