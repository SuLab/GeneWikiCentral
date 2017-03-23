"use strict";
angular.module("cyViewerApp", ["ngCookies", "ngResource", "ngSanitize", "ngRoute", "ngAnimate", "ui.bootstrap", "angular-underscore", "colorpicker.module", "angularSpinner"]).config(["$routeProvider", function(a) {
    a.when("/", {
        templateUrl: "views/main.html",
        controller: "MainCtrl"
    }).otherwise({
        redirectTo: "/"
    })
}]), angular.module("cyViewerApp").controller("MainCtrl", ["$scope", "$http", "$location", "$routeParams", "$window", "Network", "VisualStyles", function(a, b, c, d, e, f, g) {
    function h() {
        var b = angular.element(q);
        b.on("dragenter", function(a) {
            a.stopPropagation(), a.preventDefault()
        }), b.on("dragover", function(a) {
            a.stopPropagation(), a.preventDefault()
        }), b.on("drop", function(b) {
            b.preventDefault();
            var c = b.originalEvent.dataTransfer.files,
                d = c[0],
                e = new FileReader;
            e.onload = function(b) {
                var c = JSON.parse(b.target.result),
                    d = "Unknown";
                for (o = c.data, void 0 !== o && void 0 !== o.name && (d = o.name, a.currentNetworkData = o); _.contains(a.networkNames, d);) d += "*";
                a.$apply(function() {
                    a.networks[d] = c, a.networkNames.push(d), a.currentNetwork = d
                }), a.cy.load(c.elements), k()
            }, e.readAsText(d)
        })
    }

    function i(b) {
        a.nodes = o.elements.nodes, a.edges = o.elements.edges, m(b);
        var c = o.data.name;
        a.networks[c] || (a.networks[c] = o, a.networkNames.push(c), a.currentNetwork = o.data.name), j(), d.bgcolor && (a.bg.color = d.bgcolor)
    }

    function j() {
        a.columnNames = [], a.edgeColumnNames = [], a.networkColumnNames = [];
        var b = a.nodes[0];
        for (var c in b.data) a.columnNames.push(c);
        var d = a.edges[0];
        for (var e in d.data) a.edgeColumnNames.push(e);
        for (var f in o.data) a.networkColumnNames.push(f)
    }

    function k() {
        a.selectedNodes = {}, a.selectedEdges = {}
    }

    function l() {
        a.selectedNodes = {}, a.selectedEdges = {};
        var b = !1;
        a.cy.on("select", "node", function(c) {
            var d = c.cyTarget.id();
            a.selectedNodes[d] = c.cyTarget, b = !0
        }), a.cy.on("select", "edge", function(c) {
            var d = c.cyTarget.id();
            a.selectedEdges[d] = c.cyTarget, b = !0
        }), a.cy.on("unselect", "node", function(c) {
            var d = c.cyTarget.id();
            delete a.selectedNodes[d], b = !0
        }), a.cy.on("unselect", "edge", function(c) {
            var d = c.cyTarget.id();
            delete a.selectedEdges[d], b = !0
        }), setInterval(function() {
            b && a.browserState.show && (a.$apply(), b = !1)
        }, 300), //added by Julia to pregenerated code from cytoscape
        //keyed on target id
        //
        a.cy.on('tap', 'edge', function (evt) {
         // a query should be added here to populate these dictionaries
         var wdPropURL = 'https://www.wikidata.org/wiki/Property:'
         var propertyDict = {'determination method':'<a href="'+wdPropURL+'P459">determination method</a>',
                             'reference URL':'<a href="'+wdPropURL+'P854">reference URL</a>',
                             'stated in':'<a href="'+wdPropURL+'P248">stated in</a>',
                             'imported from':'<a href="'+wdPropURL+'P143">imported from</a>',
                             'retrieved':'<a href="'+wdPropURL+'P813">retrieved</a>',
                             'UniProt ID':'<a href="'+wdPropURL+'P352">UniProt ID</a>',
                             'language of work or name':'<a href="'+wdPropURL+'P407">language of work or name</a>',
                             'Entrez Gene ID':'<a href="'+wdPropURL+'P351">Entrez Gene ID</a>',
                             'NDF-RT ID':'<a href="'+wdPropURL+'P2115">NDF-RT ID</a>',
                             'Guide to Pharmacology Ligand ID':'<a href="'+wdPropURL+'P595">Guide to Pharmacology Ligand ID</a>',
                             'Disease Ontology ID':'<a href="'+wdPropURL+'P699">Disease Ontology ID</a>',
                             'software version':'<a href="'+wdPropURL+'P348">software version</a>',
                             'publication date':'<a href="'+wdPropURL+'P577">publication date</a>',
                             'as':'<a href="'+wdPropURL+'P794">as</a>',
                             'use':'<a href="'+wdPropURL+'P366">use</a>',
                             }
         var edgeQualifierDictionary = {75:propertyDict['determination method'], //disease to gene
                                        76:propertyDict['determination method'], //gene to disease
                                        77:'', //protein to gene
                                        78:'',//gene to protein
                                        79:'',//taxon to gene
                                        80:'',//taxon to disease
                                        81:'',//drug to compound
                                        82:'',//drug to disease
                                        83:propertyDict['as']+', '+propertyDict['use'],//drug to protein
                                        84:'',//compound to drug
                                        85:'',//compound to disease
                                        86:propertyDict['as']+', '+propertyDict['use'],//compound to protein
                                        87:'',//protein family to protein
                                        88:'',//repeat to protein
                                        89:'',//PTM to protein
                                        90:'',//protein binding domain to protein
                                        91:'',//conserved site to protein
                                        92:'',//binding site to protein
                                        93:'',//active site to protein
                                        }
         var edgeReferenceDictionary = {75:propertyDict['reference URL']+', '+propertyDict['stated in']+', '+propertyDict['imported from']+', '+ propertyDict['retrieved'], //disease to gene
                                        76:propertyDict['reference URL']+', '+propertyDict['stated in']+', '+propertyDict['imported from']+', '+ propertyDict['retrieved'], //gene to disease
                                        77:propertyDict['stated in']+', '+propertyDict['UniProt ID']+', '+propertyDict['retrieved']+', '+propertyDict['language of work or name'], //protein to gene
                                        78:propertyDict['stated in']+', '+propertyDict['UniProt ID']+', '+propertyDict['retrieved']+', '+propertyDict['language of work or name'],//gene to protein
                                        79:propertyDict['Entrez Gene ID']+', '+propertyDict['stated in']+', '+propertyDict['imported from']+', '+ propertyDict['retrieved'],//taxon to gene
                                        80:propertyDict['stated in']+', '+propertyDict['Disease Ontology ID'],//taxon to disease
                                        81:'',//drug to compound
                                        82:propertyDict['stated in']+', '+propertyDict['NDF-RT ID']+', '+propertyDict['language of work or name']+', '+propertyDict['retrieved'],//drug to disease
                                        83:propertyDict['stated in']+', '+propertyDict['Guide to Pharmacology Ligand ID']+', '+propertyDict['language of work or name']+', '+propertyDict['retrieved'],//drug to protein
                                        84:'',//compound to drug
                                        85:'',//compound to disease
                                        86:propertyDict['stated in']+', '+propertyDict['Guide to Pharmacology Ligand ID']+', '+propertyDict['language of work or name']+', '+propertyDict['retrieved'],//compound to protein
                                        87:propertyDict['stated in']+', '+propertyDict['imported from']+', '+propertyDict['software version']+', '+propertyDict['publication date']+', '+propertyDict['reference URL'],//protein family to protein
                                        88:propertyDict['stated in']+', '+propertyDict['imported from']+', '+propertyDict['software version']+', '+propertyDict['publication date']+', '+propertyDict['reference URL'],//repeat to protein
                                        89:propertyDict['stated in']+', '+propertyDict['imported from']+', '+propertyDict['software version']+', '+propertyDict['publication date']+', '+propertyDict['reference URL'],//PTM to protein
                                        90:propertyDict['stated in']+', '+propertyDict['imported from']+', '+propertyDict['software version']+', '+propertyDict['publication date']+', '+propertyDict['reference URL'],//protein binding domain to protein
                                        91:propertyDict['stated in']+', '+propertyDict['imported from']+', '+propertyDict['software version']+', '+propertyDict['publication date']+', '+propertyDict['reference URL'],//conserved site to protein
                                        92:propertyDict['stated in']+', '+propertyDict['imported from']+', '+propertyDict['software version']+', '+propertyDict['publication date']+', '+propertyDict['reference URL'],//binding site to protein
                                        93:propertyDict['stated in']+', '+propertyDict['imported from']+', '+propertyDict['software version']+', '+propertyDict['publication date']+', '+propertyDict['reference URL']//active site to protein
                                       }

         if (evt.cyTarget.id() in edgeQualifierDictionary) {
             var edgeWindow = window.open("", "_blank", "toolbar=no,scrollbars=no,resizable=yes,top=500,left=500,width=400,height=200")
             edgeWindow.document.write("<p>Qualifier Properties:</p><p>"+edgeQualifierDictionary[evt.cyTarget.id()]+"</p><br><p>Reference Properties:</p><p>"+edgeReferenceDictionary[evt.cyTarget.id()]+"</p>")  
         } else {
             alert(evt.cyTarget.id())
         }
        })
    }
    
    function m(b) {
        _.each(b, function(b) {
            a.visualStyles[b.title] = b, a.visualStyleNames.push(b.title)
        }), a.currentVS = r
    }
    var n, o, p = "filelist.json",
        q = "#network",
        r = "default";
    a.LAYOUTS = ["preset", "cola", "random", "grid", "circle", "concentric", "breadthfirst", "cose"], a.networks = {}, a.currentVS = null, a.visualStyles = [], a.visualStyleNames = [], a.networkNames = [], a.currentNetworkData = null, a.browserState = {
        show: !1
    }, a.overlayState = {
        show: !0
    }, a.toolbarState = {
        show: !0
    }, a.bg = {
        color: "#FAFAFA"
    }, a.columnNames = [], a.edgeColumnNames = [], a.networkColumnNames = [];
    var s = {
        showOverlay: !1,
        minZoom: .01,
        maxZoom: 200,
        boxSelectionEnabled: !0,
        layout: {
            name: "preset"
        },
        ready: function() {
            a.cy = this, a.cy.load(o.elements), g.query({
                filename: n
            }, function(b) {
                i(b), h(), l(), a.currentVS = r, a.currentLayout = "preset", a.cy.style().fromJson(a.visualStyles[r].style).update(), angular.element(".loading").remove()
            })
        }
    };
    a.toggleTableBrowser = function() {
        a.browserState.show = !a.browserState.show
    }, a.toggleOverlay = function() {
        a.overlayState.show = !a.overlayState.show
    }, a.toggleToolbar = function() {
        a.toolbarState.show = !a.toolbarState.show
    }, a.fit = function() {
        a.cy.fit()
    }, a.switchVS = function() {
        var b = a.currentVS.trim(),
            c = a.visualStyles[b].style;
        a.cy.style().fromJson(c).update()
    }, a.switchNetwork = function() {
        var b = a.networks[a.currentNetwork];
        o = f.get({
            filename: b
        }, function(b) {
            a.cy.load(b.elements), a.currentNetworkData = o, k(), a.nodes = b.elements.nodes, a.edges = b.elements.edges, j()
        })
    }, a.switchLayout = function() {
        var b = {
            name: a.currentLayout
        };
        a.cy.layout(b)
    }, b.get(p).success(function(b) {
        n = b.style;
        var c = null;
        _.each(_.keys(b), function(d) {
            "style" !== d && (null === c && (c = d), a.networks[d] = b[d], a.networkNames.push(d))
        }), o = f.get({
            filename: a.networks[c]
        }, function() {
            angular.element(q).cytoscape(s), a.currentNetworkData = o, a.currentNetwork = c
        })
    })
}]), angular.module("cyViewerApp").factory("Network", ["$resource", function(a) {
    return a("data/:filename", {
        filename: "@filename"
    })
}]), angular.module("cyViewerApp").factory("VisualStyles", ["$resource", function(a) {
    return a("data/:filename", {
        filename: "@filename"
    })
}]);

