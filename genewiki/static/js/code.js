$.getJSON("/static/json/cyto.json", function (data) { // on dom ready
      // Create a jGrowl
window.createGrowl = function(id, ttxt, type, persistent) {

    var target = $('.qtip.jgrowl:visible:last');
    
    $('<div/>').qtip({
        content: {
            text: ttxt,
            title: {
                text: 'Item Features for '+id,
                button: true
            }
        },
        position: {
            target: [10,10],
            container: $('#qtip-growl-container')
        },
        show: {
            event: false,
            ready: true,
            effect: function() {
                $(this).stop(0, 1).animate({ height: 'toggle' }, 400, 'swing');
            },
            delay: 0,
            persistent: persistent
        },
        hide: {
            event: 'click',
            effect: function(api) {
                $(this).stop(0, 1).animate({ height: 'toggle' }, 400, 'swing');
            }
        },
        style: {
            width: 250,
            classes: 'jgrowl qtip-blue qtip-shadow',
            tip: false
        },
        events: {
            render: function(event, api) {
                if(!api.options.show.persistent) {
                    $(this).bind('mouseover mouseout', function(e) {
                        var lifespan = 5000;

                        clearTimeout(api.timer);
                        if (e.type !== 'mouseover') {
                            api.timer = setTimeout(function() { api.hide(e) }, lifespan);
                        }
                    })
                    .triggerHandler('mouseout');
                }
            }
        }
    });
}
      var cy = cytoscape({
        container: document.getElementById('cy'),
	elements: data,
        style: cytoscape.stylesheet()
          .selector('node')
            .css({
	      'background-color': '#99e6ff',
              'content': 'data(label)',
              'font-size': 20        
            })
          .selector('edge')
            .css({
              'target-arrow-shape': 'triangle',
              'line-color': '#ddd',
              'target-arrow-color': '#ddd',
              'curve-style': 'bezier',
              'font-size': 20,
              'color': '#737373',
              'label': 'data(label)'
             })
          .selector(':selected')
            .css({
             'background-color': '#1ac6ff',
             'line-color': '#999999',
             'target-arrow-color': '#999999',
             'source-arrow-color': '#999999',
             'opacity': 1
          }),


        layout: {
           name: 'circle',
           directed: true,
           padding: 10
        }
      });
      cy.on('mouseover', 'node', function(event) {
        var target = event.cyTarget;
        var count = target.data('count');
        target.qtip({
          content: count,
          position: {
            my: 'top center',
            at: 'center center'
          },
          show: {
            event: event.type, 
            ready: true
         },
         hide: {
            event: 'mouseout unfocus'
         },
         style: {
            classes: 'qtip-light qtip-shadow'
         }
      }, event);
      

       cy.nodes().unbind('click').on('click', function(evt){
                console.log( 'clicked ' + evt.cyTarget.id() );
                ttext = '<table><tr><th>Statement Property</th><th>Subject Count</th><th>Object Count</th><th>Target Class</th></tr><tr><td>P361 (part of)</td><td>1</td><td>1</td><td>cellular protein metabolic process</td></tr></table>'
                createGrowl(evt.cyTarget.id(), ttext);
                //var nodeWindow = window.open("", "_blank", "toolbar=no,scrollbars=yes,resizable=yes,top=500,left=500,width=400,height=200")
                //nodeWindow.document.write("<table><tr><td>Statement Property</td><td>Count</td></tr>"+"</table><br><table><tr><td>Identifier Property</td><td>Count</td></tr>"+"</table>"

      });
      cy.edges().unbind('click').on('click', function(evt){
                console.log( 'clicked ' + evt.cyTarget.id() );
                createGrowl(evt.cyTarget.id(), 'edge');
                //var nodeWindow = window.open("", "_blank", "toolbar=no,scrollbars=yes,resizable=yes,top=500,left=500,width=400,height=200")
                //nodeWindow.document.write("<table><tr><td>Statement Property</td><td>Count</td></tr>"+"</table><br><table><tr><td>Identifier Property</td><td>Count</td></tr>"+"</table>"

      })
      

   
});

     
}); // on dom ready

