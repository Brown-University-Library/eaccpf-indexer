<!DOCTYPE html>
<html>
<head>
    <!-- meta -->
    <meta charset="utf-8">
    <title>EAC-CPF Quality Report - ${date}</title>
    <meta name="author" content="eScholarship Research Centre, University of Melbourne">
    <meta name="description" content="Analysis of EAC-CPF document content.">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- stylesheets -->
    <link rel="stylesheet" type="text/css" href="assets/bootstrap/bootstrap.min.css"/>
    <link rel="stylesheet" type="text/css" href="assets/screen.css" media="screen"/>
    <link rel="stylesheet" type="text/css" href="assets/datatables/demo_page.css" media="screen"/>
    <link rel="stylesheet" type="text/css" href="assets/datatables/demo_table.css" media="screen"/>
    <!-- scripts -->
    <script type="text/javascript" src="assets/jquery/jquery-1.9.1.min.js"></script>
    <script type="text/javascript" src="assets/bootstrap/bootstrap.min.js"></script>
    <script type="text/javascript" src="assets/datatables/jquery.dataTables.min.js"></script>
    <script type="text/javascript" src="assets/d3/d3.v2.js"></script>
</head>
<body>

<div class="container-fluid">
    <div class="row-fluid">
        <div class="span12">

            <h2>EAC-CPF Quality Report - ${date}</h2>
            <p>Data Source: ${source}</p>

            <table id="records" class="display">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Title</th>
                        <th>EntityType</th>
                        <th>LocalType</th>
                        <th>Has Abstract</th>
                        <th>Has Maintenance Record</th>
                        <th>Has Location</th>
                        <th>Errors</th>
                        <th>Content</th>
                    </tr>
                </thead>
                <tbody>
                <%
                    # find the record with the largest total content count
                    maxTotal = 0
                    for record in records:
                        if record['analysis']['the total content count'] > maxval:
                            maxTotal = record['analysis']['the total content count']
                %>
                % for record in records:
                <tr>
                    <td><a href='${record['metadata']['entityid']}'>${record['metadata']['id']}</a></td>
                    <td><a href='${record['metadata']['entityid']}'>${record['metadata']['title']}</a></td>
                    <td>${record['metadata']['entitytype']}</td>
                    <td>${record['metadata']['localtype']}</td>
                    <td>
                        % if record['analysis']['has abstract'] == True:
                            <i class="icon-ok"></i>
                        % else:
                            <i class="icon-remove"></i>
                        % endif
                    </td>
                    <td>
                        % if record['analysis']['has maintenance record'] and record['analysis']['has maintenance record'] == True:
                            <i class="icon-ok"></i>
                        % else:
                            <i class="icon-remove"></i>
                        % endif
                    </td>
                    <td>
                        % if record['analysis']['has location']:
                            <i class="icon-ok"></i>
                        % else:
                            <i class="icon-remove"></i>
                        % endif
                    </td>
                    <td>
                        <ul>
                        % for error in record['analysis']['the parsing errors']:
                            <li>${error}</li>
                        % endfor
                        </ul>
                    </td>
                    <td id='chart_${record['metadata']['id']}' class="graph"></td>
                </tr>
            % endfor
        </tbody>
        </table>

        </div><!-- /span -->
    </div><!-- /row -->
    <div class="row-fluid footer">
        <div class="span12">Copyright &copy; eScholarship Research Centre, University of Melbourne</div>
    </div>
</div><!-- /container -->


<script>
    // constructs a horizontal stacked bar graph for each record
    // @see http://tributary.io/inlet/4966973
    var records = [
        % for record in records:
            <% counts = record['analysis']['the section content counts'] %>
            {"id":"${record['metadata']['id']}", "data":[ ${counts['control']},${counts['identity']},${counts['description']},${counts['relations']}]},
        % endfor
    ];

    // construct a graph for each record
    for (var n in records) {
        var record = records[n];

        var n = 4; // number of data elements
        var m = 1; // number of records

        var stack = d3.layout.stack();
        var layers = stack(d3.range(n).map(function(d) {
              var a = [];
              for (var i = 0; i < m; ++i) {
                a[i] = {x: i, y: record['data'][d]};
              }
              return a;
            }));

        var margin = {top: 0, right: 0, bottom: 0, left: 0};
        var width = 300 - margin.left - margin.right;
        var height = 25 - margin.top - margin.bottom;

        var y = d3.scale.ordinal()
            .domain(d3.range(m))
            .range([1, height]);

        var x = d3.scale.linear()
            .domain([0, ${maxTotal}])
            .range([0, width]);

        var xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom");

        var yAxis = d3.svg.axis()
            .scale(y)
            .orient("left");

        var color = d3.scale.linear()
            .domain([0, n - 1])
            .range(["#aad", "#556"]);
        // create the svg object
        var svg = d3.select("#chart_" + record['id'])
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
        // create an element for each data item
        var layer = svg.selectAll(".layer")
            .data(layers)
            .enter().append("g")
            .attr("class", "layer")
            .style("fill", function(d, i) { return color(i); });

        layer.selectAll("rect")
            .data(function(d) { return d; })
            .enter().append("rect")
            .attr("y", function(d) { return y(d.x); })
            .attr("x", function(d) { return x(d.y0); })
            .attr("height", height)
            .attr("width", function(d) { return x(d.y); });
    }

    // initialize the data table
    $(document).ready(function() {
        $('#records').dataTable();
    });
</script>

</body>
</html>