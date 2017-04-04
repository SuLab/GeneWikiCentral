STRICT = True

BASE_SITE = 'en.wikipedia.org'

STUB_SKELETON = """{{{{Infobox_gene}}}}

'''{name}''' is a [[protein]] that in humans is encoded by the {symbol} [[gene]].{entrezcite}
{summary}

== References ==

{{{{reflist}}}}

== Further reading ==

{{{{refbegin | 2}}}}
{citations}
{{{{refend}}}}


{{{{gene{chromosome}-stub}}}}
{footer}
"""

ENTREZ_CITE = """
<ref name="entrez">
{{{{cite web
| title = Entrez Gene: {name}
| url = http://www.ncbi.nlm.nih.gov/gene/{id}
| accessdate = {currentdate}
}}}}</ref>
"""

