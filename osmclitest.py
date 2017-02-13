import osmcli, osmconfig

if __name__=="__main__":
	osmCli = osmcli.OsmCli(osmconfig.apiUrl)
	osmCli.SetUserPass(osmconfig.osmUsername, osmconfig.osmPassword)

	osmCli.CreateChangeset()
	cid = osmCli.GetCurrentChangeset()
	print cid

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
	print osmCli.Upload(createXml = createXml)

	osmCli.CloseChangeset()
	
