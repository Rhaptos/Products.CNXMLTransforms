<?xml version="1.0" encoding="UTF-8"?>
<!--
    Adds a small note to the end of an imported document containing
    a link to the original document.
-->
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:c="http://cnx.rice.edu/cnxml"
    xmlns="http://cnx.rice.edu/cnxml"
    >
<xsl:param name="url"/>
<xsl:param name="journal"/>
<xsl:param name="year"/>

<!-- Insert a note at the end of the cnxml -->
<xsl:template match="c:content">
    <xsl:copy>
        <xsl:apply-templates select="@*|node()"/>
        <xsl:if test="$url != ''">
            <note>
                <xsl:text>This article originally appeared in </xsl:text>
                <link url="{$url}">
                    <xsl:choose>
                        <xsl:when test="$journal != ''">
                            <xsl:value-of select="$journal"/>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:value-of select="$url"/>
                        </xsl:otherwise>
                    </xsl:choose>
                </link>
                <xsl:if test="$year != ''">
                    <xsl:text>, </xsl:text>
                </xsl:if>
                <xsl:value-of select="$year"/>
            </note>
        </xsl:if>
    </xsl:copy>
</xsl:template>

<!-- Identity transform for all other nodes -->
<xsl:template match="@*|node()">
    <xsl:copy>
        <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
</xsl:template>

</xsl:stylesheet>

