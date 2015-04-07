<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:doc="urn:isbn:1-931666-33-4"
                xmlns:ead="urn:isbn:1-931666-22-9"
                xmlns:ns0="http://www.esrc.unimelb.edu.au"
                xmlns:xlink="http://www.w3.org/1999/xlink"
                xmlns:str="http://exslt.org/strings"
                extension-element-prefixes="str uf"
                exclude-result-prefixes="xlink"
                version="1.0">
    <xsl:output method="text" indent="yes" encoding="UTF-8" omit-xml-declaration="yes" />

    <xsl:param name="category"/>
    <xsl:param name="container_part1"/>
    <xsl:param name="container_part2"/>
    <xsl:param name="callno"/>
    <xsl:param name="subject"/>
    <xsl:param name="raw_ead_c"/>
    <xsl:param name="wikipedia-id"/>
    <xsl:param name="bloglink"/>

    <xsl:template match="/"><xsl:value-of select="$raw_ead_c"/>
        <add>
            <doc>
	        	<!-- metadata, presentation, source values -->
	            <xsl:if test="/doc:eac-cpf/@ns0:metadata != ''">
	            	<field name="metadata_url"><xsl:value-of select="/doc:eac-cpf/@ns0:metadata" /></field>
                </xsl:if>
	            <xsl:if test="/doc:eac-cpf/@ns0:presentation != ''">
	            	<field name="presentation_url"><xsl:value-of select="/doc:eac-cpf/@ns0:presentation" /></field>
                </xsl:if>
                
	        	<!-- control -->
	            <field name="id"><xsl:value-of select="/doc:eac-cpf/doc:control/doc:recordId" /></field>
	            <xsl:if test="/doc:eac-cpf/doc:control/doc:localControl/@localType != ''">
                	<field name="localtype"><xsl:value-of select="/doc:eac-cpf/doc:control/doc:localControl/doc:term" /></field>
	            </xsl:if>
	            <xsl:for-each select="/doc:eac-cpf/doc:control/doc:localControl">
	                <field name="localtype_{@localType}"><xsl:value-of select="doc:term"/></field>
	            </xsl:for-each>
	            
	            <field name="create_date"><xsl:value-of select="/doc:eac-cpf/doc:control/doc:maintenanceHistory/doc:maintenanceEvent[doc:eventType/text()='created']/doc:eventDateTime/@standardDateTime" />T00:00:00Z</field>
	            
	            <xsl:for-each select="/doc:eac-cpf/doc:control/doc:sources/doc:source">
	            	<field name="source"><xsl:value-of select="doc:sourceEntry" /></field>
	            	<field name="source_link"><xsl:value-of select="@xlink:href"/></field>
                </xsl:for-each>
                
                <xsl:if test="$bloglink != ''">
                    <field name="info_link"><xsl:value-of select="$bloglink"/></field>
                </xsl:if>

                <xsl:if test="$wikipedia-id != ''">   
                    <field name="wiki_id"><xsl:value-of select="$wikipedia-id"/></field>
                </xsl:if>
                
	        	<!-- identity -->
	            <field name="entityId"><xsl:value-of select="/doc:eac-cpf/doc:cpfDescription/doc:identity/doc:entityId" /></field>
	            <field name="type"><xsl:value-of select="/doc:eac-cpf/doc:cpfDescription/doc:identity/doc:entityType" /></field>
	            
	            
                <xsl:for-each select="/doc:eac-cpf/doc:cpfDescription/doc:identity/doc:nameEntry/doc:part">
                    <xsl:if test="position() = 1" >
                    <field name="title" boost="{1000 div position()}">
                        <xsl:value-of select="." />
                    </field></xsl:if>
                    
                    <xsl:if test="position() &gt; 1">
                    <field name="other_title" boost="{100 div position()}">
                        <xsl:value-of select="." />
                    </field></xsl:if>
                </xsl:for-each>
                
	        	<!-- description -->
	            <xsl:if test="/doc:eac-cpf/doc:cpfDescription/doc:description/doc:existDates/doc:dateRange/doc:fromDate/@doc:standardDate != ''">
	                <field name="fromDate"><xsl:value-of select="/doc:eac-cpf/doc:cpfDescription/doc:description/doc:existDates/doc:dateRange/doc:fromDate/@doc:standardDate"/>T00:00:00Z</field>
	            </xsl:if>
	            <xsl:if test="/doc:eac-cpf/doc:cpfDescription/doc:description/doc:existDates/doc:dateRange/doc:toDate/@doc:standardDate != ''">
	                <field name="toDate"><xsl:value-of select="/doc:eac-cpf/doc:cpfDescription/doc:description/doc:existDates/doc:dateRange/doc:toDate/@doc:standardDate"/>T00:00:00Z</field>
	            </xsl:if>
                <xsl:for-each select="/doc:eac-cpf/doc:cpfDescription/doc:description/doc:functions/doc:function/doc:term">
                    <field name="function"><xsl:value-of select='.'/></field>
                </xsl:for-each>
                <!-- abstract: include all content from the biogHist -->
                <field name="abstract">
                    <xsl:for-each select="/doc:eac-cpf/doc:cpfDescription/doc:description/doc:biogHist/doc:*">
                        <xsl:value-of select="." />
                        <xsl:text> </xsl:text>
                    </xsl:for-each>
                </field>
	        	<!-- relations -->
	        	<!--TODO: Need the descriptiveNote attached to each relationEntry. -->
                <xsl:for-each select="/doc:eac-cpf/doc:cpfDescription/doc:relations/doc:cpfRelation">
                    <xsl:if test="./doc:relationEntry">
                        <field name="relation_entry"><xsl:value-of select="./doc:relationEntry" /></field>
                    </xsl:if>
                    <xsl:if test="./doc:descriptiveNote">
                        <field name="relation_note"><xsl:value-of select="./doc:descriptiveNote"/></field>
                    </xsl:if>
                    <field name="relation">
                        <xsl:if test="./doc:relationEntry">
                            <xsl:value-of select="./doc:relationEntry" />
                        </xsl:if>
                        <xsl:if test="./doc:descriptiveNote"><xsl:text> (</xsl:text><xsl:value-of select="./doc:descriptiveNote"/>)</xsl:if>
                    </field>
                </xsl:for-each>
                <xsl:for-each select="/doc:eac-cpf/doc:cpfDescription/doc:relations/doc:resourceRelation/doc:relationEntry">
                    <field name="relation"><xsl:value-of select="." /></field>
                </xsl:for-each>
                
                <!--This text is stored as abstract, but it sometimes includes HTML.-->
                <field name="biog_hist">
                    <xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
                        <xsl:value-of select="/doc:eac-cpf/doc:biogHist"/>
                    <xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
                </field>
                
                
                
                <!--Place-->
                <xsl:for-each select="/doc:eac-cpf/doc:cpfDescription/doc:description/doc:places/doc:place">
                    <field name="place"><xsl:value-of select="concat(doc:placeEntry, ' (', doc:placeRole, ')')"/></field>
                </xsl:for-each>
                       
                <!--Save parameters drawn from the EAD by Python. -->
                <xsl:if test="$subject != ''">
                    <field name="subject"><xsl:value-of select="$subject"/></field>
                </xsl:if>
                    
                <xsl:if test="$callno != ''">
                    <field name="part1_call_number"><xsl:value-of select="$callno"/></field>
                    <field name="part1_category"><xsl:value-of select="$category"/></field>
                </xsl:if>
                
                 <xsl:for-each select="str:split($container_part1, ', ')">
                    <field name="container"><xsl:value-of select="."/></field>
                    <field name="container_part1"><xsl:value-of select="."/></field>
                </xsl:for-each>
                
                <xsl:if test="$container_part1!=''">
                    <field name="collection_parts">Part I</field>
                </xsl:if>
                
                <xsl:if test="$container_part2!=''">
                    <field name="collection_parts">Part II</field>
                </xsl:if>
                
                <xsl:for-each select="str:split($container_part2, ', ')">
                    <field name="container"><xsl:value-of select="."/></field>
                    <field name="container_part2"><xsl:value-of select="."/></field>
                </xsl:for-each>
                
                <field name="raw_ead_c">
                    <xsl:value-of disable-output-escaping="yes" select="$raw_ead_c" />
                </field>
                
                <!--Save the whole record-->
                <field name="raw_eac">
                    <xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
                        <xsl:copy-of select="/doc:eac-cpf"/>
                    <xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
                </field>
	        </doc>
        </add>
    </xsl:template>
</xsl:stylesheet>