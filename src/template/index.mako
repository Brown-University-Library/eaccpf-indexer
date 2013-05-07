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
        <link rel="stylesheet" type="text/css" href="assets/bootstrap.min.css" />
        <link rel="stylesheet" type="text/css" href="assets/screen.css" media="screen" />
        <link rel="stylesheet" type="text/css" href="assets/print.css" media="print" />
        <!-- scripts -->
        <script type="text/javascript" src="assets/jquery-1.9.1.min.js"></script>
        <script type="text/javascript" src="assets/bootstrap.min.js"></script>
    </head>
    <body>
    <div class="container">
        <div class="row">
            <div class="span12">
                <h1>EAC-CPF Quality Report - ${date}</h1>
                <p>Document source ${source}</p>
                <div id="summary">
                    <h2>Summary</h2>
                    <p>Matrix diagram</p>
                </div>

                <div>
                    <h2>Records</h2>
                    <table class="records">
                    % for record in records:
                    <!--
            conformance, errors = self._isConformantToEacCpfSchema(data)
            analysis['conforms to schema'] = conformance
            analysis['has maintenance record'] = self._hasMaintenanceRecord(data)
            analysis['has record identifier'] = self._hasRecordIdentifier(data)
            analysis['has resource relations'] = self._hasResourceRelations(data)
            analysis['the entity existence dates'] = self._getExistDates(data)
            analysis['the entity type'] = self._getEntityType(data)
            analysis['the entity local type'] = self._getEntityLocalType(data)
            analysis['the parsing errors'] = errors
            analysis['the resource relations count'] = self._getResourceRelationsCount(data)
            analysis['the section content counts'] = self._getSectionContentCounts(data)
            analysis['the total content count'] = self._getTotalContentCount(data)
                    -->
                        <%
                            errors = record['analysis']['the parsing errors']
                            error_count = len(errors)
                            counts = record['analysis']['the section content counts']
                        %>
                        <tr class="record summary">
                            <td><a href='${record['metadata']['entityid']}'>${record['metadata']['id']}<a/></td>
                            <td><a href='${record['metadata']['entityid']}'>${record['metadata']['title']}</a></td>
                            <td>${record['metadata']['localtype']}</td>
                            <td>
                                % if record['analysis']['has maintenance record'] and record['analysis']['has maintenance record'] == True:
                                    <i class="icon-ok"></i>
                                % else:
                                    <i class="icon-remove"></i>
                                % endif
                            </td>
                            <td>${error_count} errors</td>
                            <td class="section-content-counts">
                                <ul class="counts">
                                    <li>${counts['control']}</li>
                                    <li>${counts['identity']}</li>
                                    <li>${counts['description']}</li>
                                    <li>${counts['relations']}</li>
                                </ul>
                            </td>
                        </tr>
                        <tr class="record detail">
                            <td>
                                <ul>
                                    % for error in errors:
                                        <li>${error}</li>
                                    % endfor
                                </ul>
                            </td>
                        </tr>
                    % endfor 
                    </table>
                </div>
                <br/>

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