<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet
  version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:exsl="http://exslt.org/common"
  extension-element-prefixes="exsl"
  exclude-result-prefixes="exsl">

<xsl:import href="pass7_cnxml_postprocessing.xsl"/>
<xsl:import href="pass8_cnxml_postprocessing.xsl"/>

<xsl:output
  method="xml"
  encoding="UTF-8"
  indent="yes"/>

<xsl:strip-space elements="*"/>

<xsl:template match="/">
  <!-- CNXML Postprocessing -->
  <xsl:variable name="temp7">
    <xsl:apply-templates select="." mode="pass7"/>
  </xsl:variable>
  <xsl:apply-templates select="exsl:node-set($temp7)" mode="pass8"/>
</xsl:template>


</xsl:stylesheet>