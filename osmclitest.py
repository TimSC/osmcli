import osmcli, osmconfig

if __name__=="__main__":
	osmCli = osmcli.OsmCli(osmconfig.apiUrl)
	osmCli.SetUserPass(osmconfig.osmUsername, osmconfig.osmPassword)

	osmCli.CreateChangeset()
	cid = osmCli.GetCurrentChangeset()
	print cid

	lat = 51.25022331526812
	lon = -0.6042092878597837
	createXml = "  <node id='-289' changeset='"+str(cid)+"' lat='"+str(lat)+"' lon='"+str(lon)+"' />\n" +\
	"  <node id='-2008' changeset='"+str(cid)+"' lat='51.2419166618214' lon='-0.5910182209303836' />\n"+\
	"  <way id='-2010' changeset='"+str(cid)+"'>\n"+\
	"    <nd ref='-289' />\n"+\
	"    <nd ref='-2008' />\n"+\
	"  </way>\n"
	osmCli.Upload(createXml = createXml)

	osmCli.CloseChangeset()
	
