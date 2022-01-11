from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse
from wikidataintegrator import wdi_core, wdi_login, wdi_helpers
import sys 
sys.path.append('/home/ubuntu/GeneWikiCentral/genewiki')
from genewiki.wiki.views import article_create

def wiki_mapping(request, entrez_id):
    article_query = """
     SELECT ?article WHERE {
             ?cid wdt:P351 '"""+str(entrez_id)+"""' ;
                  wdt:P688 ?protein ;
                  wdt:P703 wd:Q15978631 .
             OPTIONAL { ?cid rdfs:label ?label filter (lang(?label) = "en") .}
             OPTIONAL {?genearticle schema:about ?cid ;
                          schema:inLanguage "en" .
                       FILTER (SUBSTR(str(?genearticle), 1, 25) = "https://en.wikipedia.org/") .
                       FILTER (SUBSTR(str(?genearticle), 1, 38) != "https://en.wikipedia.org/wiki/Template")}
             OPTIONAL {?proteinarticle schema:about ?protein ;
                          schema:inLanguage "en" .
                      FILTER (SUBSTR(str(?proteinarticle), 1, 25) = "https://en.wikipedia.org/") .
                      FILTER (SUBSTR(str(?proteinarticle), 1, 38) != "https://en.wikipedia.org/wiki/Template")}
             BIND(COALESCE(?genearticle, ?proteinarticle) as ?article)
             }
    """
    wikidata_results = wdi_core.WDItemEngine.execute_sparql_query(prefix=settings.PREFIX, query=article_query)['results']['bindings']
    article = ''
    for x in wikidata_results:
        article = x['article']['value']
    if wikidata_results:
        print('article found')
        return redirect(article)
    else:
        print('no article found')
        return redirect(article_create, entrez_id)
        #return redirect('genewiki.wiki.views.article_create', entrez_id)
