<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:c="http://cnx.rice.edu/cnxml"
  version="1.0">

<!-- Insert a @id for elements that require it (RED text import didn't add them) -->
<xsl:template match="
    c:para|
    c:list|
    c:meaning|
    c:definition|
    c:figure|
    c:subfigure|
    c:note|
    c:exercise|
    c:problem|
    c:solution|
    c:section">
  <xsl:copy>
    <xsl:if test="not(@id)">
      <xsl:attribute name="id">
        <xsl:value-of select="generate-id()"/>
      </xsl:attribute>
    </xsl:if>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>


<!-- Identity transform. Nothing interesting... -->
<xsl:template match="@*|node()">
  <xsl:copy>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

</xsl:stylesheet>