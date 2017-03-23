from django.shortcuts import render

from genewiki.report.queries import gene_counts, disease_counts, get_errors, get_error_month, bot_update, get_genes, get_proteins, get_mgenes, get_compounds, get_diseases

import datetime

def counts(request):

    results_genes = gene_counts('animal')
    results_microbes = gene_counts('bacteria')
    results_disease = disease_counts()
    results_update_gene = bot_update('genes')
    results_errors = get_errors()
    results_errorsm = get_error_month()
    
    vals = {}
    # test data
    # chart_data = '''
    #      [new Date(2016, 06, 10), 60058, 73450, 42079,36962],
    #      [new Date(2016, 06, 13), 70000, 80000, 50000,40000],
    #      [new Date(2016, 06, 15), 70000, 80000, 50000,40000]
    # '''
    # Overview Tab
    protein_cdata = '''
          [new Date(2016, 06, 10), 60058],
          [new Date(2016, 06, 13), 70000],
          [new Date(2016, 06, 15), 74000]
    '''
    compound_cdata = '''
          [new Date(2016, 06, 10), 60058],
          [new Date(2016, 06, 13), 70000],
          [new Date(2016, 06, 15), 74000]
    '''
    ontology_cdata = '''
          [new Date(2016, 06, 10), 60058],
          [new Date(2016, 06, 13), 70000],
          [new Date(2016, 06, 15), 74000]
    '''

    table_data = '''
          ['Genes', 60000, 'SELECT'],
          ['Microbial Genes', 60000, 'SELECT'],
          ['Proteins', 200000, 'SELECT'],
          ['DiseaseOntology', 50000, 'SELECT'],
          ['Compounds', 6000, 'SELECT']
    '''
    # Jenkins Error Tab
    jenkins_change_bar = '''
        ['Event', '8-16-2016', '8-24-2016'],
        ['merged', 500, 200],
        ['deleted', 100, 30],
        ['updated', 2000, 10000],
        ['created', 0, 25]
    ''' 
    #jenkins_pie = '''
    #    ['Error', 'Types per Run'],
    #    ['Script',     11],
    #    ['Update',      2],
    #    ['Mistyped',  2],
    #    ['Deletion', 2]
    #''' 
    # jenkins_table = '''
    #     ['gene', 'null value',  'Value Not Found ...', '8-10-2016', 'Q123940'],
    #     ['disease', 'data type',  'Mismatch datatype...','8-10-2016', 'Q1283748'],
    #     ['protein', 'key error',  'key value error occurred in...', '8-16-2016', 'Q1294472']
    #''' 
    # Curation Issues Tab
    curation_table = '''
        ['gene', 'Mismerge', 'protein gene merged', '8-10-2016', 'http://wikidata.fixme'],
        ['microbe', 'Misformed', 'statements with incorrect identifiers', '8-10-2016', 'http://wikidata.fixme'],
        ['disease', 'Mismerge', 'protein gene merged', '8-12-2016', 'http://wikidata.fixme']
    ''' 
    curation_pie = '''
        ['Error', 'Types per Run'],
        ['Script',     11],
        ['Update',      2],
        ['Mistyped',  2],
        ['Deletion', 2]
    '''
    
    vals['gene_cdata'], vals['gene_clegend'] =  stackedbar_chart(results_genes)
    vals['microbe_cdata'], vals['microbe_clegend'] = stackedbar_chart(results_microbes)
    vals['disease_cdata'], vals['disease_clegend'] = stackedbar_chart(results_disease)
    # vals['cdata'] = chart_data #for testing
    vals['protein_cdata'] = protein_cdata
    vals['compound_cdata'] = compound_cdata
    #vals['ontology_cdata'] = ontology_cdata
    vals['tdata'] = overview_table
    vals['genebar'] = jenkins_update(results_update_gene)
    vals['jbar'] = jenkins_change_bar
    vals['jpie'] = jenkins_pie(results_errorsm)
    vals['jtable'] = jenkins_table(results_errors)
    vals['ctable'] = curation_table
    vals['cpie'] = curation_pie 

    return render(request, 'report/stats.jade', vals)


def line_chart(results):
    curdate = ''
    chart_data = ''
    legend = ''  # creates key
    unique_species = {}  # finds unique species
    for date in sorted(results.keys()):
        # add formatted data to string for google charts
        for species in sorted(results[date].keys()):  # need to sort to be sure generating same data lines for the chart
            ccount = str(results[date][species])
            species_name = species.replace(" ", "_")
            # get the month and subtract 1 charts index months from 0
            cdate = str(date).split("-")
            cdate_mm = "0" + str(int(cdate[1]) - 1)
            cdate_yyyy = cdate[0]
            day_time = cdate[2].split(" ")
            cdate_dd = day_time[0]
            if(curdate != date):
                chart_data += '[new Date(%s, %s, %s), %s, ' % (cdate_yyyy, cdate_mm, cdate_dd, ccount)
            else:
                chart_data += '%s, ' % (ccount)
            if species not in unique_species:
                legend += '''data.addColumn('number', '%s');\n''' % (species_name)
            curdate = date
            unique_species[str(species)] = 1
        # remove last comma and space
        chart_data = chart_data[:-2]
        chart_data += '],\n'
    return chart_data, legend


def stackedbar_chart(results):
    curdate = ''
    chart_data = ''
    legend = '''['Rank','''  # creates key
    unique_species = {}  # finds unique species

    # first count all species (or classes called species below but could also be class in the case of bacteria)
    for date in sorted(results.keys()):
        for species in sorted(results[date].keys()):
            unique_species[str(species)] = 1

    # create legend string
    for species in sorted(unique_species):
        if species == '':
            species_name = 'unspecified'
        else:
            species_name = species.replace(" ", "_").capitalize()
        legend += ''' '%s',''' % (species_name)    # add legend data
    legend += '],\n'
	   
    for date in sorted(results.keys()):
        # add formatted data to string for google charts
        for species in sorted(unique_species):  # need to sort to be sure generating same data lines for the chart
	    # get the month and subtract 1 charts index months from 0
            cdate = str(date).split("-")
            cdate_mm = "0" + str(int(cdate[1]) - 1)
            cdate_yyyy = cdate[0]
            day_time = cdate[2].split(" ")
            cdate_dd = day_time[0]
            if species in results[date]:
                ccount = str(results[date][species])
            else:
                ccount = '0'
            if(curdate != date):
                chart_data += '[new Date(%s, %s, %s), %s, ' % (cdate_yyyy, cdate_mm, cdate_dd, ccount)
            else:
                chart_data += '%s, ' % (ccount)
            curdate = date
        # remove last comma and space
        chart_data = chart_data[:-2]
        chart_data += '],\n'
    return chart_data, legend

def overview_table():
    gene_no, gene_query = '','' #get_genes()
    mgene_no, mgene_query = '',''#get_mgenes()
    protein_no, protein_query ='',''#get_proteins()
    disease_no, disease_query = '',''#get_diseases()
    compound_no, compound_query = '',''#get_compounds()
    table_data = '''
          ['Genes', %s, '%s'],
          ['Microbial Genes', %s, '%s'],
          ['Proteins', %s, '%s'],
          ['DiseaseOntology', %s, '%s'],
          ['Compounds', %s, '%s']
    ''' % (gene_no, gene_query, mgene_no, mgene_query, protein_no, protein_query, disease_no, disease_query, compound_no, compound_query)
    return table_data

def jenkins_update(results):
    chart_data = '''['Event', '''
    rotated_dict = {}
    unique_date = {}
    curtype = ''
    for row in results:
        # add back in once really querying data
        # date = row['update_date'].strftime('%m-%d-%Y')
        date = row['update_date']
        update_type = row['update_type']
        if rotated_dict.get(update_type) is None:
            rotated_dict[row['update_type']] = {}
        rotated_dict[row['update_type']][date]=row['count']
        unique_date[date] = 1

    # this creates the event displayed in legend
    for date in sorted(unique_date):
        chart_data +=''''%s', ''' % date    

    for update_type in sorted(rotated_dict.keys()):
        for date in sorted(unique_date.keys()):
            if rotated_dict[update_type].get(date) is None:
                count = 0
            else:
                count = rotated_dict[update_type][date]
            if curtype != update_type:
                chart_data += '''],\n['%s', %s''' % (update_type, count)
                curtype = update_type
            else:
                chart_data += ''', %s''' % (count) 
    chart_data += '],\n'
    return chart_data


def jenkins_table(results):
   table_data = ''
   for row in results:
       table_data += '''['%s', '%s', '%s', '%s', '%s'],\n''' % (row['bot'], row['error_class'], row['error_message'], row['date'], row['qid'])
       
   return table_data


def jenkins_pie(results):
   chart_data = '''['Error', 'Types per Run'],\n'''
   error_counts = dict()

   for row in results:
       if row['error_class'] in error_counts:
           error_counts[row['error_class']] += 1
       else:
           error_counts[row['error_class']] = 1
   for etype in error_counts:
       chart_data += '''['%s', %s],\n''' % (etype, error_counts[etype])

   return chart_data           
