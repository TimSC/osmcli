import urlutil

class OsmCli(object):
	def __init__(self, apiUrl):	
		self.apiUrl = apiUrl
		self.openChangeSet = None
		self.userpass = None

	def SetUserPass(self, username, password):
		self.userpass = username+":"+password

	def GetCurrentChangeset(self):
		return self.openChangeSet

	def CreateChangeset(self, comment=None):
		if self.openChangeSet is not None:
			raise RuntimeError("Only one open changeset is supported")

		#Create a changeset
		createChangeset = "<?xml version='1.0' encoding='UTF-8'?>\n" +\
			"<osm version='0.6' generator='OsmCli'>\n" +\
			"  <changeset  id='0' open='false'>\n"
		if comment is not None:
			createChangeset + "    <tag k='comment' v='{}' />\n".format(comment)
		
		createChangeset += "    <tag k='created_by' v='OsmCli' />\n" +\
			"  </changeset>\n" +\
			"</osm>\n"

		response = urlutil.Put(self.apiUrl+"/0.6/changeset/create",createChangeset,self.userpass)
		if urlutil.HeaderResponseCode(response[1]) != "HTTP/1.1 200 OK": 
			raise RuntimeError("Error creating changeset: " + response[0])
		self.openChangeSet = int(response[0])

	def CloseChangeset(self):
		if self.openChangeSet is None:
			raise RuntimeError("Changeset is not open")

		#Close the changeset
		response = urlutil.Put(self.apiUrl+"/0.6/changeset/"+str(self.openChangeSet)+"/close","",self.userpass)
		if urlutil.HeaderResponseCode(response[1]) != "HTTP/1.1 200 OK": 
			raise RuntimeError ("Error closing changeset: " + response[0])

		self.openChangeSet = None

	def Upload(self, createXml = None, modifyXml = None, deleteXml = None):
		if self.openChangeSet is None:
			raise RuntimeError("Changeset is not open")

		create = "<?xml version='1.0' encoding='UTF-8'?>\n" +\
			"<osmChange version='0.6' generator='OsmCli'>\n"
		if createXml is not None:
			create += "<create>\n{}</create>\n".format(createXml)
		if modifyXml is not None:
			create += "<modify>\n{}</modify>\n".format(modifyXml)
		if deleteXml is not None:
			create += "<delete>\n{}</delete>\n".format(deleteXml)
		create += "</osmChange>\n"
		response = urlutil.Post(self.apiUrl+"/0.6/changeset/"+str(self.openChangeSet)+"/upload",create,self.userpass)
		if urlutil.HeaderResponseCode(response[1]) != "HTTP/1.1 200 OK": 
			raise RuntimeError ("Error uploading data: "+ response[0])
		
		print response[0]

