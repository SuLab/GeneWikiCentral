from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.conf import settings
from pprint import pprint
from django.views.decorators.clickjacking import xframe_options_exempt


from genewiki.wiki.textutils import create, interwiki_link
from genewiki import pbb_secret
import urllib.parse, mwclient

from wikidataintegrator import wdi_core, wdi_login, wdi_helpers, wdi_settings

@require_http_methods(['GET', 'POST'])
@xframe_options_exempt
def article_create(request, entrez_id):
    results = create(entrez_id)
    # We failed to gather information then return the ID error
    if results is None:
        return HttpResponse('Invalid or missing Entrez Identifier')

    titles = results.get('titles')
    title = wiki_title(entrez_id)

    vals = {'results': results,
            #'article': article,
            'titles': titles,
            'title': title,
            'entrez': entrez_id}
    pprint(vals)
    if request.method == 'POST':
        print('This method is ' + str(request.method))
       
        # Only assign this 'title' var internally if the online article status is False (not a Wikipedia page)
        uploadopt = request.POST.get('page_type')
        if uploadopt is None:
            print('uploadopt')
            return HttpResponse('Must select title option.')

        title = titles[uploadopt][0] if titles[uploadopt][1] is False else None

        # The page title that they wanted to create is already online
        if title is None:
            return HttpResponse('Article or template already exists.')

        vals['title'] = title
        content = results['stub']
        print('about to write')
        write(vals['title'],content)
        # create corresponding talk page with appropriate project banners
        talk_title = 'Talk:{0}'.format(title)
        talk_content = """{{WikiProjectBannerShell|
                          {{WikiProject Gene Wiki|class=stub|importance=low}}
                          {{Wikiproject MCB|class=stub|importance=low}}
                          }}"""
        write(talk_title, talk_content)
        # create interwiki link
        interwiki_link(entrez_id, title)
        # save article again
        write(vals['title'],content)
        print('maybe just wrote')
        return redirect(article_create, entrez_id)


    return render(request, 'wiki/create.html', vals)


def wiki_title(entrez_id):
    article_query = """
        SELECT ?article WHERE {
        ?cid wdt:P351 '""" + str(entrez_id) + """'.
        ?cid wdt:P703 wd:Q15978631 .
        OPTIONAL { ?cid rdfs:label ?label filter (lang(?label) = "en") .}
        ?article schema:about ?cid .
        ?article schema:inLanguage "en" .
        FILTER (SUBSTR(str(?article), 1, 25) = "https://en.wikipedia.org/") .
        FILTER (SUBSTR(str(?article), 1, 38) != "https://en.wikipedia.org/wiki/Template")
        }
        limit 1
    """
    wikidata_results = wdi_core.WDItemEngine.execute_sparql_query(prefix=settings.PREFIX, query=article_query)['results']['bindings']
    article = ''
    for x in wikidata_results:
        article = x['article']['value']

    if wikidata_results:
        if article is not None:
            title = article.split("/")
            str_title = urllib.parse.unquote(title[-1])
            return str_title

def write(title, text, summary=None):
    '''
        Writes the wikitext representation of the created page to wikipedia
    '''
    username = pbb_secret.username
    password = pbb_secret.password
    site = mwclient.Site(('https', 'en.wikipedia.org'))
    site.login(username, password)
    page = site.Pages[title]

    try:
        result = page.save(text, summary, minor=True)

    except MwClientError:
        client.captureException
