<?xml version="1.0" encoding="UTF-8"?>
<!-- 
	EAC-CPF to Apache Solr Input Document Format Transform
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
    <xsl:output method="text" indent="yes" encoding="UTF-8" omit-xml-declaration="yes" />
    <xsl:template match="/">
        <add>
	        <doc>
	        	<!-- control -->
	            <field name="id"><xsl:value-of select="/eac-cpf/control/recordId" /></field>
	            <xsl:if test="/eac-cpf/control/localControl/@localType != ''">
	            	<field name="localtype"><xsl:value-of select="/eac-cpf/control/localControl/term" /></field>
	            </xsl:if>
	        	<!-- identity -->
	            <field name="entityId"><xsl:value-of select="/eac-cpf/cpfDescription/identity/entityId" /></field>
	            <field name="type"><xsl:value-of select="/eac-cpf/cpfDescription/identity/entityType" /></field>
	            <field name="title">
                    <xsl:for-each select="/doc:eac-cpf/doc:cpfDescription/doc:identity/doc:nameEntry/doc:part">
                        <xsl:value-of select="." />
                        <xsl:text> </xsl:text>
                    </xsl:for-each>
                </field>
	        	<!-- description -->
	            <xsl:if test="/eac-cpf/cpfDescription/description/existDates/dateRange/fromDate/@standardDate != ''">
	                <field name="fromDate"><xsl:value-of select="/eac-cpf/cpfDescription/description/existDates/dateRange/fromDate/@standardDate"/>T00:00:00Z</field>
	            </xsl:if>
	            <xsl:if test="/eac-cpf/cpfDescription/description/existDates/dateRange/toDate/@standardDate != ''">
	                <field name="toDate"><xsl:value-of select="/eac-cpf/cpfDescription/description/existDates/dateRange/toDate/@standardDate"/>T00:00:00Z</field>
	            </xsl:if>
                <xsl:apply-templates select="functions" />
                <!-- abstract: will appear in /biogHist or /biogHist/abstract -->
                <xsl:choose>
                    <xsl:when test="/eac-cpf/cpfDescription/description/biogHist/abstract">
                        <field name="abstract"><xsl:value-of select="/eac-cpf/cpfDescription/description/biogHist/abstract" /></field>
                    </xsl:when>
                    <xsl:otherwise>
	                    <field name="abstract"><xsl:value-of select="/eac-cpf/cpfDescription/description/biogHist" /></field>
                    </xsl:otherwise>
                </xsl:choose>
	        	<!-- relations -->
	        </doc>                
        </add>
    </xsl:template>

    <xsl:template name="functions" match="/doc:eac-cpf/doc:cpfDescription/doc:description/doc:functions/doc:function">
        <field name="function"><xsl:value-of select="doc:term"/></field>
    </xsl:template>

</xsl:stylesheet>