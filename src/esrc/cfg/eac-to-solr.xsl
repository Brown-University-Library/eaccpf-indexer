<?xml version="1.0" encoding="UTF-8"?>
<!-- 
	EAC to Apache Solr Input Document Format Transform
	Copyright 2013 eScholarship Research Centre, University of Melbourne
	
	Licensed under the Apache License, Version 2.0 (the "License");
	you may not use this file except in compliance with the License.
	You may obtain a copy of the License at
	
	    http://www.apache.org/licenses/LICENSE-2.0
	
	Unless required by applicable law or agreed to in writing, software
	distributed under the License is distributed on an "AS IS" BASIS,
	WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
	See the License for the specific language governing permissions and
	limitations under the License.
-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <xsl:template match="/">
        <add>
	        <doc>
	        	<!-- control -->
	            <field name="id"><xsl:value-of select="/eac/control/id" /></field>
	        	<!-- identity -->
	            <field name="title"><xsl:value-of select="/eac/identity/nameEntry/part" /></field>
	            <field name="type"><xsl:value-of select="/eac/identity/entityType" /></field>
	        	<!-- description -->
	            <field name="abstract"><xsl:value-of select="/eac/description/biogHist/abstract" /></field>
	            <xsl:if test="/eac/description/existDates/fromDate/@standardForm != ''">
	                <field name="fromDate_StandardForm"><xsl:apply-templates select="/eac/description/existDates/fromDate/@standardForm"/></field>
	            </xsl:if>
	            <xsl:if test="/eac/description/existDates/toDate/@standardForm != ''">
	                <field name="toDate_StandardForm"><xsl:apply-templates select="/eac/description/existDates/toDate/@standardForm"/></field>
	            </xsl:if>
	            <field name="function"><xsl:value-of select="/eac/description/function/descNote"/></field>            
	        	<!-- relations -->
	            <xsl:for-each select="/eac/relations/cpfRelation"><field name="cpfRelation_relationLink"><xsl:value-of select="relationLink"/></field></xsl:for-each>
	            <xsl:for-each select="/eac/relations/resourceRelation">
	                <field name="resourceRelation_natureOfRelation"><xsl:value-of select="natureOfRelation" /></field>
	                <field name="resourceRelation_name"><xsl:value-of select="relationXMLWrap/bib/name" /></field>
	                <field name="resourceRelation_title"><xsl:value-of select="relationXMLWrap/bib/title" /></field>
	                <field name="resourceRelation_publisher"><xsl:value-of select="relationXMLWrap/bib/imprint/publisher"/></field>
	            </xsl:for-each>
	        </doc>                
        </add>
    </xsl:template>
    
    <!-- Transform EAC StandardForm date from YYYYMMDD format to Solr compatible YYYY-MM-DDThh:mm:ssZ format -->
    <xsl:template match="@standardForm"><xsl:value-of select="substring(.,1,4)" />-<xsl:value-of select="substring(.,5,2)" />-<xsl:value-of select="substring(.,7,2)" />T00:00:00Z</xsl:template>
    
    <!-- Transform EAC Date from YYYY format to Solr compatible YYYY-MM-DDThh:mm:ssZ format -->
    <xsl:template match="date">
        <xsl:choose>
            <xsl:when test="substring(.,1,1) = 'c'"></xsl:when>
            <xsl:when test="contains(.,'/')"><field name="resourceRelation_publicationDate"><xsl:call-template name="token-delimited-date"><xsl:with-param name="token" select="'/'"></xsl:with-param></xsl:call-template></field></xsl:when>
            <xsl:when test="contains(.,'-')"><field name="resourceRelation_publicationDate"><xsl:call-template name="token-delimited-date"><xsl:with-param name="token" select="'-'"></xsl:with-param></xsl:call-template></field></xsl:when>
            <!-- We assume that the value is YYYY here. -->
            <!-- <xsl:otherwise><xsl:value-of select="."/>-01-01T00:00:00Z TO <xsl:value-of select="."/>-12-31T23:59:59Z</xsl:otherwise> -->
            <xsl:otherwise><field name="resourceRelation_publicationDate"><xsl:value-of select="."/>-01-01T00:00:00Z</field></xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <!-- Transform dates of the form YYYY-YYYY to a Solr compatible date range -->
    <xsl:template name="date-range-format"></xsl:template>

    <!-- Transform dates of the form ????/??/?? to a Solr compatible YYYY-MM-DDThh:mm:ssZ format. -->
    <xsl:template name="token-delimited-date">
        <xsl:variable name="token" select="'/'" />
        <xsl:variable name="slashes">
            <xsl:call-template name="countTokens">
                <xsl:with-param name="string" select="." />
                <xsl:with-param name="token" select="$token" />
                <xsl:with-param name="result" select="0" />
            </xsl:call-template>
        </xsl:variable>
        <xsl:choose>
            <!-- YYYY/M -->
            <xsl:when test="string-length(.) = 6"><xsl:value-of select="substring(.,1,4)" />-0<xsl:value-of select="substring(.,6,1)" />-00T00:00:00Z</xsl:when>
            <!-- YYYY/MM -->
            <xsl:when test="string-length(.) = 7 and $slashes = 1"><xsl:value-of select="substring(.,1,4)" />-<xsl:value-of select="substring(.,6,2)" />-00T00:00:00Z</xsl:when>
            <!-- YYYY/M/D --> 
            <xsl:when test="string-length(.) = 8 and $slashes = 2"><xsl:value-of select="substring(.,1,4)" />-0<xsl:value-of select="substring(.,6,1)" />-0<xsl:value-of select="substring(.,8,1)" />T00:00:00Z</xsl:when>
            <!-- YYYY/M/DD or YYYY/MM/D -->
            <xsl:when test="string-length(.) = 9 and $slashes = 2">
                <xsl:choose>
                    <!-- YYYY/MM/D -->
                    <xsl:when test="substring(.,8,1) = '/'"><xsl:value-of select="substring(.,1,4)" />-<xsl:value-of select="substring(.,6,2)" />-0<xsl:value-of select="substring(.,9,1)" />T00:00:00Z</xsl:when>
                    <!-- YYYY/M/DD -->
                    <xsl:otherwise><xsl:value-of select="substring(.,1,4)" />-0<xsl:value-of select="substring(.,6,1)" />-<xsl:value-of select="substring(.,8,2)" />T00:00:00Z</xsl:otherwise>
                </xsl:choose>
            </xsl:when>
            <!-- YYYY/MM/DD -->
            <xsl:when test="string-length(.) = 10 and $slashes = 2"><xsl:value-of select="substring(.,1,4)" />-<xsl:value-of select="substring(.,6,2)" />-<xsl:value-of select="substring(.,9,2)" />T00:00:00Z</xsl:when>
            <!-- FAIL -->
            <!-- <xsl:otherwise>0001-01-01T00:00:00Z</xsl:otherwise> -->
        </xsl:choose>
    </xsl:template>
    
    <!-- Count instances of a token in a string -->
    <xsl:template name="countTokens">
        <xsl:param name="string" />
        <xsl:param name="token" />
        <xsl:param name="result" />
        <xsl:choose>
            <xsl:when test="contains($string, $token)">
                <xsl:call-template name="countTokens">
                    <xsl:with-param name="string" select="substring-after($string, $token)" />
                    <xsl:with-param name="token" select="$token"/>
                    <xsl:with-param name="result" select="$result + 1"/>
                </xsl:call-template>  
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="$result" />
            </xsl:otherwise>
        </xsl:choose>       
    </xsl:template>
    
</xsl:stylesheet>
