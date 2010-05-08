<?xml version="1.0" encoding="UTF-8"?>
<!-- Extracts additional authors and collaborators in a SWORD mets.xml file
     and outputs a JSON dictionary.
  -->
<!-- This file contains portions of code from http://code.google.com/p/xml2json-xslt -->
<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:bib="http://bibtexml.sf.net/"
  >
  <xsl:output indent="no" omit-xml-declaration="yes" method="text" encoding="UTF-8" media-type="text/x-json"/>

  <xsl:param name="json.textkey">_text</xsl:param>
  <xsl:param name="json.printroot" select="0"/>


<xsl:template name="json.convert.pair">
	<xsl:param name="key">
		<xsl:call-template name="json.escape.string">
			<xsl:with-param name="s" select="name()"/>
		</xsl:call-template>
	</xsl:param>
	<xsl:param name="value">
		<xsl:apply-templates select="@*|node()"/>
    </xsl:param>
	<xsl:value-of select="$key"/>
    <xsl:text>:</xsl:text>
    <xsl:value-of select="$value"/>
</xsl:template>

<!--
  Copyright (c) 2006, Doeke Zanstra
  All rights reserved.

  Redistribution and use in source and binary forms, with or without modification, 
  are permitted provided that the following conditions are met:

  Redistributions of source code must retain the above copyright notice, this 
  list of conditions and the following disclaimer. Redistributions in binary 
  form must reproduce the above copyright notice, this list of conditions and the 
  following disclaimer in the documentation and/or other materials provided with 
  the distribution.

  Neither the name of the dzLib nor the names of its contributors may be used to 
  endorse or promote products derived from this software without specific prior 
  written permission.

  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
  ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. 
  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, 
  INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
  BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF 
  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
  OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF 
  THE POSSIBILITY OF SUCH DAMAGE.
-->
  <xsl:strip-space elements="*"/>


  <!-- Main template for escaping strings; used by above template and for object-properties 
       Responsibilities: placed quotes around string, and chain up to next filter, json.escape.bs -->
  <xsl:template name="json.escape.string">
    <xsl:param name="s"/>
    <xsl:text>"</xsl:text>
    <xsl:call-template name="json.escape.bs">
      <xsl:with-param name="s" select="$s"/>
    </xsl:call-template>
    <xsl:text>"</xsl:text>
  </xsl:template>
  
  <!-- Escape the backslash (\) before everything else. -->
  <xsl:template name="json.escape.bs">
    <xsl:param name="s"/>
    <xsl:choose>
      <xsl:when test="contains($s,'\')">
        <xsl:call-template name="json.escape.quot">
          <xsl:with-param name="s" select="concat(substring-before($s,'\'),'\\')"/>
        </xsl:call-template>
        <xsl:call-template name="json.escape.bs">
          <xsl:with-param name="s" select="substring-after($s,'\')"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:call-template name="json.escape.quot">
          <xsl:with-param name="s" select="$s"/>
        </xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  
  <!-- Escape the double quote ("). -->
  <xsl:template name="json.escape.quot">
    <xsl:param name="s"/>
    <xsl:choose>
      <xsl:when test="contains($s,'&quot;')">
        <xsl:call-template name="json.encode.bs">
          <xsl:with-param name="s" select="concat(substring-before($s,'&quot;'),'\&quot;')"/>
        </xsl:call-template>
        <xsl:call-template name="json.escape.quot">
          <xsl:with-param name="s" select="substring-after($s,'&quot;')"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:call-template name="json.encode.bs">
          <xsl:with-param name="s" select="$s"/>
        </xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  
  <!-- Replace tab, line feed and/or carriage return by its matching escape code. Can't escape backslash
       or double quote here, because they don't replace characters (&#x0; becomes \t), but they prefix 
       characters (\ becomes \\). Besides, backslash should be seperate anyway, because it should be 
       processed first. This function can't do that. -->
  <xsl:template name="json.encode.bs">
    <xsl:param name="s"/>
    <xsl:choose>
      <!-- tab -->
      <xsl:when test="contains($s,'&#x9;')">
        <xsl:call-template name="json.encode.bs">
          <xsl:with-param name="s" select="concat(substring-before($s,'&#x9;'),'\t',substring-after($s,'&#x9;'))"/>
        </xsl:call-template>
      </xsl:when>
      <!-- line feed -->
      <xsl:when test="contains($s,'&#xA;')">
        <xsl:call-template name="json.encode.bs">
          <xsl:with-param name="s" select="concat(substring-before($s,'&#xA;'),'\n',substring-after($s,'&#xA;'))"/>
        </xsl:call-template>
      </xsl:when>
      <!-- carriage return -->
      <xsl:when test="contains($s,'&#xD;')">
        <xsl:call-template name="json.encode.bs">
          <xsl:with-param name="s" select="concat(substring-before($s,'&#xD;'),'\r',substring-after($s,'&#xD;'))"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise><xsl:value-of select="$s"/></xsl:otherwise>
    </xsl:choose>
  </xsl:template>









  <!-- ignore document text -->
  <xsl:template match="text()[../@* or preceding-sibling::node() or following-sibling::node()]">
  	<!-- Uniquely identify the text node key. Otherwise, it's invalid JSON -->
  	<xsl:variable name="textkey">
  		<xsl:value-of select="$json.textkey"/>
  		<xsl:if test="count(parent::node()/text())>1 and position()>1">
  			<xsl:value-of select="position()"/>
  		</xsl:if>
  	</xsl:variable>
    <xsl:call-template name="json.escape.string">
      <xsl:with-param name="s" select="$textkey"/>
    </xsl:call-template>
  	<xsl:text>:</xsl:text>
    <xsl:call-template name="json.escape.string">
      <xsl:with-param name="s" select="."/>
    </xsl:call-template>
    <xsl:if test="following-sibling::node()">
    	<xsl:text>,</xsl:text>
    </xsl:if>
  </xsl:template>

  <!-- string -->
  <xsl:template match="text()">
    <xsl:call-template name="json.escape.string">
      <xsl:with-param name="s" select="."/>
    </xsl:call-template>
  </xsl:template>


  <!-- number (no support for javascript mantise) -->
  <xsl:template match="text()[not(string(number())='NaN' or
                       (starts-with(.,'0' ) and . != '0'))]">
    <xsl:value-of select="."/>
  </xsl:template>

  <!-- boolean, case-insensitive -->
  <xsl:template match="text()[translate(.,'TRUE','true')='true']">true</xsl:template>
  <xsl:template match="text()[translate(.,'FALSE','false')='false']">false</xsl:template>

<xsl:template match="@*">
	<xsl:call-template name="json.convert.pair">
		<xsl:with-param name="value">
 				<xsl:call-template name="json.escape.string">
 					<xsl:with-param name="s" select="."/>
 				</xsl:call-template>
 			</xsl:with-param>			
	</xsl:call-template>
</xsl:template>

  <!-- object -->
<xsl:template match="*" name="json.convert.element">
	<xsl:variable name="name" select="name()"/>
	<xsl:variable name="arrayMember" select="preceding-sibling::*[name()=$name]"/>
	<!-- Skip elements of the array since they are matched explicitly below -->
	<xsl:if test="not($arrayMember)">
		<xsl:apply-templates select="." mode="json.convert.element.intern"/>
	</xsl:if>
</xsl:template>

<xsl:template match="*" mode="json.convert.element.intern">
	<xsl:variable name="name" select="name()"/>
	<xsl:variable name="arrayMember" select="preceding-sibling::*[name()=$name]"/>
	<xsl:variable name="arrayTail" select="not(following-sibling::*[name()=$name])"/>
	<xsl:variable name="arrayHead" select="not($arrayMember) and not($arrayTail)"/>

	<xsl:if test="not($arrayMember) and (not(.=/*) or $json.printroot)">
	    <xsl:call-template name="json.escape.string">
	      <xsl:with-param name="s" select="name()"/>
	    </xsl:call-template>
	    <xsl:text>:</xsl:text>
	</xsl:if>

	<xsl:if test="$arrayHead">
		<xsl:text>[</xsl:text>
	</xsl:if>

	<xsl:if test="$arrayMember">
		<xsl:text>,</xsl:text>
	</xsl:if>
		
    <xsl:variable name="complex" select="count(@*|*)>0"/>
	<xsl:if test="$complex">
		<xsl:text>{</xsl:text>
	</xsl:if>
	<!-- Write out @* -->
	<xsl:variable name="has-children" select="count(node())>0"/>
	<xsl:for-each select="@*">
		<xsl:apply-templates select="."/>
		<xsl:if test="position()!=last() or $has-children">
			<xsl:text>,</xsl:text>
		</xsl:if>
	</xsl:for-each>
	<!-- If empty and no attributes, print null -->
	<xsl:if test="not(@* or child::node() or text())">
		<xsl:text>null</xsl:text>
	</xsl:if>
	<!-- Write out child nodes -->
	<xsl:apply-templates select="node()"/>
	
	<xsl:if test="$complex">
		<xsl:text>}</xsl:text>
	</xsl:if>
    
    <!-- Write out the elements of the array -->
    <xsl:if test="$arrayHead">
    	<xsl:apply-templates mode="json.convert.element.intern" select="following-sibling::*[name()=$name]"/>
    	<xsl:text>]</xsl:text>
    </xsl:if>

	<xsl:if test="(following-sibling::*[name()!=$name] or following-sibling::text()) and not($arrayMember)">
		<xsl:text>,</xsl:text>
	</xsl:if>

</xsl:template>

  
  <!-- convert root element to an anonymous container -->
  <xsl:template match="/">
    <xsl:apply-templates select="node()"/>
  </xsl:template>


</xsl:stylesheet>