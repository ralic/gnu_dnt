<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!-- Output settings -->
  <xsl:output method="xml"
	      omit-xml-declaration="no"
	      indent="yes"/>

  <!-- Global variables -->
  <xsl:variable name="newLine">
    <xsl:text>
    </xsl:text>
  </xsl:variable>

  <!-- Main -->
  <xsl:template match="/root">
    <todo>
      <xsl:if test="$dt_version">
	<xsl:attribute name="version">
	  <xsl:value-of select="$dt_version"/>
	</xsl:attribute>
      </xsl:if>
      <xsl:value-of select="$newLine"/>
      <xsl:if test="normalize-space(text()) != ''">
	<title>
	  <xsl:value-of select="text()"/>
	</title>
      </xsl:if>
      <xsl:for-each select="child::*">
	<xsl:call-template name="nodeProcess"/>
      </xsl:for-each>
    </todo>
  </xsl:template>

  <!-- SubNodes Process  -->
  <xsl:template name="subnodesProcess">
    <xsl:for-each select="child::*">
      <xsl:if test="name() = 'entry'">
	<xsl:call-template name="nodeProcess"/>
      </xsl:if>
    </xsl:for-each>
  </xsl:template>

  <!-- Node Process -->
  <xsl:template name="nodeProcess">
    <note>
      <xsl:if test="@priority">
	<xsl:attribute name="priority">
	  <xsl:value-of select="@priority"/>
	</xsl:attribute>
      </xsl:if>
      <xsl:if test="@start">
	<xsl:attribute name="time">
	  <xsl:value-of select="@start"/>
	</xsl:attribute>
      </xsl:if>
      <xsl:if test="@end">
	<xsl:attribute name="done">
	  <xsl:value-of select="@end"/>
	</xsl:attribute>
      </xsl:if>
      <xsl:value-of select="text()"/>
      <xsl:if test="@end">
	<xsl:if test="comment">
	  <comment>
	    <xsl:variable name="c">
	      <xsl:value-of select="comment"/>
	    </xsl:variable>
	    <xsl:value-of select="$c"/>
	  </comment>
	</xsl:if>
      </xsl:if>
      <xsl:call-template name="subnodesProcess"/>
    </note>
    <xsl:value-of select="$newLine"/>
  </xsl:template>
</xsl:stylesheet>
