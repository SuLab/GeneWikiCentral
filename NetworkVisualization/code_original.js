$(function(){ // on dom ready
      var cy = cytoscape({
        container: document.getElementById('cy'),

        style: cytoscape.stylesheet()
          .selector('node')
            .css({
	      'background-color': '#99e6ff',
              'content': 'data(id)'
            })
          .selector('edge')
            .css({
              'target-arrow-shape': 'triangle',
              'line-color': '#ddd',
              'target-arrow-color': '#ddd',
              'curve-style': 'bezier',
              'font-size': 10,
              'color': '#737373',
              'label': 'data(label)'
             }),

        elements: {
	    nodes: [
                { data: { id: 'gene' } },
                { data: { id: 'protein' } },
                { data: { id: 'taxon' } },
                { data: { id: 'disease' } },
                { data: { id: 'chemical compound' } }
            ], 
      
            edges: [
               { data: { id: 'gene"protein', source: 'gene', target: 'protein', label: 'Encoded by (P702)' } },
	       { data: { id: 'protein"gene', source: 'protein', target: 'gene', label: 'Encodes (P688)' } },
               { data: { id: 'protein"chemical compound', source: 'protein', target: 'chemical compound', label: "mm" } },
               { data: { id: 'gene"disease', source: 'gene', target: 'disease', label: 'mm' } },
               { data: { id: 'gene"taxon', source: 'gene', target: 'taxon', label: 'test'} }
           ]
        },
        layout: {
           name: 'breadthfirst',
           directed: true,
           roots: '#a',
           padding: 10
        }
      });
}); // on dom ready
