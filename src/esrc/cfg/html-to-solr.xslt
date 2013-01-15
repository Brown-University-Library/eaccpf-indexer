<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<!--
  If there is an EAC file present, get the title and body fields from the EAC.
  Else, get the title and body fields from the HTML document.

 -->
<xsl:template match="/">
<add>
  <doc>
    <field name="uri"><xsl:value-of select="//meta[@name='DC.Identifier']/@content" /></field> 
    <field name="title"><xsl:value-of select="//meta[@name='DC.Title']/@content" /></field>
    <field name="text"><xsl:value-of select="//body" /></field>
  </doc>
</add>
</xsl:template>

</xsl:stylesheet>