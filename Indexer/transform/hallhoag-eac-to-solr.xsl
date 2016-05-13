<?xml version="1.0" ?>
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

    <xsl:template match="/">
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
                    <field name="outside_resource"><xsl:value-of select="." /></field>
                </xsl:for-each>
                
                <!--This text is stored as abstract, but it sometimes includes HTML.-->
                <field name="biog_hist">
                    <xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
                        <xsl:value-of select="/doc:eac-cpf/doc:biogHist"/>
                    <xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
                </field>
                
                <!--Place-->
                <xsl:for-each select="/doc:eac-cpf/doc:cpfDescription/doc:description/doc:places/doc:place">
                    <field name="place"><xsl:value-of select="doc:placeEntry"/></field>
                </xsl:for-each>
                       
                <xsl:if test="//doc:localDescriptions/doc:localDescription/doc:term[@vocabularySource='Broad']">
                    <field name="broad_category"><xsl:value-of select="//doc:localDescriptions/doc:localDescription/doc:term[@vocabularySource='Broad']"/></field>
                </xsl:if>
                
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