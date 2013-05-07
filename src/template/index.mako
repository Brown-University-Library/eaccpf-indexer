<!DOCTYPE html>
<html>
    <head>
        <!-- meta -->
        <meta charset="utf-8">
        <title>${title}</title>
        <meta name="author" content="eScholarship Research Centre, University of Melbourne">
        <meta name="description" content="Analysis of EAC-CPF document content.">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <!-- stylesheets -->
        <link rel="stylesheet" type="text/css" href="assets/bootstrap/bootstrap.min.css" />
        <link rel="stylesheet" type="text/css" href="assets/screen.css" media="screen" />
        <link rel="stylesheet" type="text/css" href="assets/print.css" media="print" />
        <!-- scripts -->
        <script type="text/javascript" src="assets/jquery-1.9.1.min.js"></script>
        <script type="text/javascript" src="assets/bootstrap/bootstrap.min.js"></script>
        <script type="text/javascript" src="assets/highcharts.js"></script>
    </head>
    <body>
        
    <div class="container">
        <div class="row">
            <div class="span12">
                <h1>EAC-CPF Quality Report - ${date}</h1>
                <p>Document source ${source}</p>
                <div id="summary">
                    <h3>Summary</h3>
                    <p>Matrix diagram</p>
                </div>
           </div>
		</div>
		
		<div class="row">
			<div class="span12">
                <h3>Records</h3>
                % for record in records:
                    <%
                        errors = record['analysis']['the parsing errors']
                        error_count = len(errors)
                        counts = record['analysis']['the section content counts']
                    %>
                    <div class="row record">
                    	<div class="summary">
                            <div class="span1"><a href='${record['metadata']['entityid']}'>${record['metadata']['id']}<a/></div>
                            <div class="span4"><a href='${record['metadata']['entityid']}'>${record['metadata']['title']}</a></div>
                            <div class="span1">${record['metadata']['localtype']}</div>
                            <div class="span1">
                                % if record['analysis']['has maintenance record'] and record['analysis']['has maintenance record'] == True:
                                    <i class="icon-ok"></i>
                                % else:
                                    <i class="icon-remove"></i>
                                % endif
                            </div>
                            <div class="span1">${error_count}</div>
                            <div class="span3 graph">
                            	<div id="chart_${loop.index}"></div>
								<script>
								$(function () {
        $('#chart_${loop.index}').highcharts({
            chart: {
            	animation: false,
            	borderWidth: 0,
            	height: 50,
            	margin: 0,
            	plotBorderWidth: 0,
            	spacingBottom: 0,
            	spacingLeft: 0,
            	spacingRight: 0,
            	spacingTop: 0,
                type: 'bar',
                width: 300,
            },
            legend: {
            	enabled: false,
            },
            plotOptions: {
                series: {
                    stacking: 'normal'
                }
            },
            series: [
            	{ data: [ ${counts['control']}     ] },
            	{ data: [ ${counts['identity']}    ] },
            	{ data: [ ${counts['description']} ] }, 
            	{ data: [ ${counts['relations']}   ] },
            ],
            title: {
            	text: null,
            },
            yAxis: {
                min: 0,
            },
        });
    });
								
								</script>
                            </div>
                        </div>
                        <div class="row detail">
                        	Error list here
                        </div>
                    </div>
                % endfor 
            </div>
        </div>
    </div>

    <div class="container" style="margin-bottom:40px">
        <div class="row">
            <div class="span12">Copyright &copy; 2013 eScholarship Research Centre, University of Melbourne</div>
        </div>
    </div>
    
    </body>
</html>