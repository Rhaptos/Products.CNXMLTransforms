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
    <xsl:variable name="title">
        <xsl:choose>
            <xsl:when test="$journal != ''">
                <xsl:value-of select="$journal"/>
            </xsl:when>
            <xsl:when test="$url != ''">
                <xsl:value-of select="$url"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:text>Another source</xsl:text>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:variable>
    <xsl:copy>
        <xsl:apply-templates select="@*|node()"/>
        <note>
            <xsl:text>This article originally appeared in </xsl:text>
            <xsl:choose>
                <xsl:when test="$url != ''">
                    <link url="{$url}">
                        <xsl:value-of select="$title"/>
                    </link>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="$title"/>
                </xsl:otherwise>
            </xsl:choose>
            <xsl:if test="$year != ''">
                <xsl:text>, </xsl:text>
            </xsl:if>
            <xsl:value-of select="$year"/>
        </note>
    </xsl:copy>
</xsl:template>

<!-- Identity transform for all other nodes -->
<xsl:template match="@*|node()">
    <xsl:copy>
        <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
</xsl:template>

</xsl:stylesheet>

