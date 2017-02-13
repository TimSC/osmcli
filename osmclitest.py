import osmcli, osmconfig

if __name__=="__main__":
	osmCli = osmcli.OsmCli(osmconfig.apiUrl)
	osmCli.SetUserPass(osmconfig.osmUsername, osmconfig.osmPassword)

	osmCli.CreateChangeset()

	lat = 51.25022331526812
	lon = -0.6042092878597837
	createXml = "  <create>" +\
	"  <node id='-289' lat='"+str(lat)+"' lon='"+str(lon)+"' />\n" +\
	"  <node id='-2008' lat='51.2419166618214' lon='-0.5910182209303836' />\n"+\
	"  <way id='-2010'>\n"+\
	"    <nd ref='-289' />\n"+\
	"    <nd ref='-2008' />\n"+\
	"  </way>\n" +\
	"  </create>\n"
	
	diffNodes, diffWays, diffRelations = osmCli.Upload(createXml = createXml)
	firstNodeInfo = diffNodes[-289]
	firstWayInfo = diffWays[-2010]

	osmCli.CloseChangeset()
	
	osmCli.CreateChangeset()

	modifyXml = "<modify>\n"+\
	"  <node id='{}' version='{}' lat='{}' lon='{}' />\n".format(firstNodeInfo[0],firstNodeInfo[1],lat+0.1,lon)+\
	"</modify>\n"

	diffNodes, diffWays, diffRelations = osmCli.Upload(modifyXml = modifyXml)

	deleteXml = "<delete>\n"+\
	"  <way id='{}' version='{}'/>\n".format(firstWayInfo[0], firstWayInfo[1])+\
	"</delete>\n"

	diffNodes, diffWays, diffRelations = osmCli.Upload(deleteXml = deleteXml)

	osmCli.CloseChangeset()

