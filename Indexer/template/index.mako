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
    <link rel="stylesheet" type="text/css" href="assets/bootstrap/bootstrap.min.css"/>
    <link rel="stylesheet" type="text/css" href="assets/screen.css" media="screen"/>
    <!-- scripts -->
    <script type="text/javascript" src="assets/jquery-1.9.1.min.js"></script>
    <script type="text/javascript" src="assets/jquery.dataTables.min.js"></script>
    <script type="text/javascript" src="assets/bootstrap/bootstrap.min.js"></script>
    <script type="text/javascript" src="assets/d3.v2.js"></script>
</head>
<body>

<div class="container-fluid">
    <div class="row-fluid">
        <div class="span12">
            <h2>EAC-CPF Quality Report - ${date}</h2>
            <p>Data Source: ${source}</p>
            <table id="records">
                <tbody>
                <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>LocalType</th>
                    <th>Maintenance Record</th>
                    <th>Location</th>
                    <th>Warnings</th>
                    <th>Errors</th>
                    <th>Content</th>
                </tr>

                % for record in records:
                <%
                    errors = record['analysis']['the parsing errors']
                    error_count = len(errors)
                    counts = record['analysis']['the section content counts']
                %>
                <tr>
                    <td><a href='${record['metadata']['entityid']}'>${record['metadata']['id']}</a></td>
                    <td><a href='${record['metadata']['entityid']}'>${record['metadata']['title']}</a></td>
                    <td>${record['metadata']['localtype']}</td>
                    <td>
                        % if record['analysis']['has maintenance record'] and record['analysis']['has maintenance record'] == True:
                            <i class="icon-ok"></i>
                        % else:
                            <i class="icon-remove"></i>
                        % endif
                    </td>
                    <td>-</td>
                    <td>-</td>
                    <td>
                        <ul>
                        % for error in errors:
                            <li>${error}</li>
                        % endfor
                        </ul>
                    ${error_count}
                    </td>
                    <td id='chart_${record['metadata']['entityid']}' class="graph"></td>
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
        {"id":"E000033", "control":3000, "identity":4000, "description":5000, "relations":5000 },
        {"id":"E000454", "control":3000, "identity":3000, "description":3000, "relations":5000 },
        {"id":"E000097", "control":12000, "identity":5000, "description":13000, "relations":5000 },
        {"id":"E000016", "control":8000, "identity":21000, "description":11000, "relations":5000 },
        {"id":"E000435", "control":30000, "identity":12000, "description":8000, "relations":5000 },
        {"id":"E000432", "control":26614, "identity":6944, "description":30778, "relations":5000 },
        {"id":"E000038", "control":8000, "identity":12088, "description":20000, "relations":5000 }
    ];
    // the largest total
    var maxtotal = 10000;

    for (var i in records) {
        var record = records[i]; // the record
        var n = 4; // number of layers
        var m = 1; // number of samples per layer

        // convert the record values into an array
        var id = record['id'];
        var layers = d3.layout.stack(d3.range(n).map(function(d) {
            return [
                { 'x':0, 'y':record['control'] },
                { 'x':1, 'y':record['identity'] },
                { 'x':2, 'y':record['description'] },
                { 'x':3, 'y':record['relations'] }
            ];
        }));

        //the largest single layer
        var yGroupMax = d3.max(layers, function(layer) { return d3.max(layer, function(d) { return d.y; }); });

        //the largest stack
        var yStackMax = d3.max(layers, function(layer) { return d3.max(layer, function(d) { return d.y0 + d.y; }); });

        var margin = {top: 0, right: 0, bottom: 0, left: 0};
        var width = 300 - margin.left - margin.right;
        var height = 24 - margin.top - margin.bottom;

        var y = d3.scale.ordinal()
            .domain([0,1])
            .range([0, height]);

        var x = d3.scale.linear()
            .domain([0, maxtotal])
            .range([0, width]);

        var color = d3.scale.linear()
            .domain([0, n - 1])
            .range(["#aad", "#556"]);

        var svg = d3.select("body").append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        svg.selectAll(".bar")
            .data(layers)
            .enter().append("rect")
            .style("fill", function(d, i) { return color(i); })
            .attr("y", 0)
            .attr("x", function(d) { return x(d.y0); })
            .attr("height", height)
            .attr("width", function(d) { return x(d.y); });

        var yAxis = d3.svg.axis()
            .scale(y)
            .tickSize(1)
            .tickPadding(6)
            .orient("left");

        svg.append("g")
            .attr("class", "y axis")
            .call(yAxis);
    }
</script>


</body>
</html>