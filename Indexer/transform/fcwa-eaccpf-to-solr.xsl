<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:doc="urn:isbn:1-931666-33-4"
                xmlns:ns0="http://www.esrc.unimelb.edu.au"
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
	            	<field name="presentation_url">https://www.facp.esrc.unimelb.edu.au/guide/wa/<xsl:value-of select="/doc:eac-cpf/doc:control/doc:recordId" /></field>
                </xsl:if>
	            <xsl:if test="/doc:eac-cpf/@ns0:source != ''">
	            	<field name="source"><xsl:value-of select="/doc:eac-cpf/@ns0:source" /></field>
                </xsl:if>
	        	<!-- control -->
	            <field name="id"><xsl:value-of select="/doc:eac-cpf/doc:control/doc:recordId" /></field>
	            <xsl:if test="/doc:eac-cpf/doc:control/doc:localControl/@localType != ''">
	            	<field name="localtype"><xsl:value-of select="/doc:eac-cpf/doc:control/doc:localControl/doc:term" /></field>
	            </xsl:if>
	        	<!-- identity -->
	            <field name="entityId"><xsl:value-of select="/doc:eac-cpf/doc:cpfDescription/doc:identity/doc:entityId" /></field>
	            <field name="type"><xsl:value-of select="/doc:eac-cpf/doc:cpfDescription/doc:identity/doc:entityType" /></field>
	            <field name="title"><xsl:value-of select="/doc:eac-cpf/doc:cpfDescription/doc:identity/doc:nameEntry/doc:part" /></field>
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
                <!-- abstract: will appear in /biogHist or /biogHist/abstract -->
                <xsl:choose>
                    <xsl:when test="/doc:eac-cpf/doc:cpfDescription/doc:description/doc:biogHist/doc:abstract">
                        <field name="abstract"><xsl:value-of select="/doc:eac-cpf/doc:cpfDescription/doc:description/doc:biogHist/doc:abstract" /></field>
                    </xsl:when>
                    <xsl:otherwise>
	                    <field name="abstract"><xsl:value-of select="/doc:eac-cpf/doc:cpfDescription/doc:description/doc:biogHist" /></field>
                    </xsl:otherwise>
                </xsl:choose>
	        	<!-- relations -->
	        </doc>
        </add>
    </xsl:template>
</xsl:stylesheet>