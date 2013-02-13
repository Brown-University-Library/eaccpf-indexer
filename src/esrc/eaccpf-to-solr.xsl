<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <xsl:template match="/">
        <add>
	        <doc>
	            <field name="id"><xsl:value-of select="/eac-cpf/control/recordId" /></field>
	            <xsl:if test="/eac-cpf/control/localControl/@localType != ''">
	            	<field name="localtype"><xsl:value-of select="/eac-cpf/control/localControl/term" /></field>
	            </xsl:if>
	            <field name="entityId"><xsl:value-of select="/eac-cpf/cpfDescription/identity/entityId" /></field>
	            <field name="type"><xsl:value-of select="/eac-cpf/cpfDescription/identity/entityType" /></field>
	            <field name="title"><xsl:value-of select="/eac-cpf/cpfDescription/identity/nameEntry/part" /></field>
	            <xsl:if test="/eac-cpf/cpfDescription/description/existDates/dateRange/fromDate/@standardDate != ''">
	                <field name="fromDate"><xsl:value-of select="/eac-cpf/cpfDescription/description/existDates/dateRange/fromDate/@standardDate"/>T00:00:00Z</field>
	            </xsl:if>
	            <xsl:if test="/eac-cpf/cpfDescription/description/existDates/dateRange/toDate/@standardDate != ''">
	                <field name="toDate"><xsl:value-of select="/eac-cpf/cpfDescription/description/existDates/dateRange/toDate/@standardDate"/>T00:00:00Z</field>
	            </xsl:if>
	            <xsl:for-each select="/eac-cpf/cpfDescription/description/functions/function">
	            	<field name="function"><xsl:value-of select="term"/></field>            
	            </xsl:for-each>
	        </doc>                
        </add>
    </xsl:template>    
</xsl:stylesheet>
