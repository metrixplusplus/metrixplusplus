<?xml version="1.0" encoding="WINDOWS-1251" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/TR/WD-xsl">
<xsl:template match="/">
<table border="1">
<tr bgcolor="#CCCCCC">
<td align="center"><strong>Function</strong></td>
<td align="center"><strong>Change</strong></td>
<td align="center"><strong>Checksum</strong></td>
</tr>
<xsl:for-each select="swi:report/swi:module/swi:file/swi:function">
<tr bgcolor="#F5F5F5">
<td><xsl:value-of select="swi:name"/></td>
<td align="right"><xsl:value-of select="swi:modification"/></td>
<td><xsl:value-of select="swi:statistic/swi:checksum/swi:source/swi:exact"/></td>
</tr>
</xsl:for-each>
</table>
</xsl:template>
</xsl:stylesheet>