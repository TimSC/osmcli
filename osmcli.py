import urlutil
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
class GoneError(RuntimeError):
	pass

class OsmCli(object):
	def __init__(self, apiUrl):	
		self.apiUrl = apiUrl
		self.openChangeSet = None
		self.userpass = None

	def SetUserPass(self, username, password):
		self.userpass = username+":"+password

	def GetCurrentChangeset(self):
		return self.openChangeSet

	def CreateChangeset(self, comment=None, source=None):
		if self.openChangeSet is not None:
			raise RuntimeError("Only one open changeset is supported")

		#Create a changeset
		createChangeset = "<?xml version='1.0' encoding='UTF-8'?>\n" +\
			"<osm version='0.6' generator='OsmCli'>\n" +\
			"  <changeset  id='0' open='false'>\n"
		if comment is not None:
			createChangeset + "    <tag k='comment' v='{}' />\n".format(escape(comment))
		if source is not None:
			createChangeset + "    <tag k='source' v='{}' />\n".format(escape(source))
		
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

		query = ET.Element('osmChange')
		query.text = "\n"
		query.attrib["version"] = "0.6"
		query.attrib["generator"] = "OsmCli"

		if createXml is not None:
			xmldoc = ET.fromstring(createXml)
			xmldoc.tag = "create"
			xmldoc.tail = "\n"
			for nd in xmldoc: #Add changeset id info
				nd.attrib["changeset"] = str(self.openChangeSet)
			query.append(xmldoc)

		if modifyXml is not None:
			xmldoc = ET.fromstring(modifyXml)
			xmldoc.tag = "modify"
			xmldoc.tail = "\n"
			for nd in xmldoc: #Add changeset id info
				nd.attrib["changeset"] = str(self.openChangeSet)
			query.append(xmldoc)

		if deleteXml is not None:
			xmldoc = ET.fromstring(deleteXml)
			xmldoc.tag = "delete"
			xmldoc.tail = "\n"
			for nd in xmldoc: #Add changeset id info
				nd.attrib["changeset"] = str(self.openChangeSet)
			query.append(xmldoc)

		response = urlutil.Post(self.apiUrl+"/0.6/changeset/"+str(self.openChangeSet)+"/upload", 
			ET.tostring(query, encoding="utf8"),self.userpass)
		if urlutil.HeaderResponseCode(response[1]) != "HTTP/1.1 200 OK": 
			raise RuntimeError ("Error uploading data: "+ response[0])
		
		#Process diff result
		diffNodes, diffWays, diffRelations = {}, {}, {}
		xmlroot = ET.fromstring(response[0])
		for nd in xmlroot:
			if nd.tag == "node":
				if "new_id" in nd.attrib:
					diffNodes[int(nd.attrib["old_id"])] = map(int, (nd.attrib["new_id"], nd.attrib["new_version"]))
				else:
					diffNodes[int(nd.attrib["old_id"])] = None
			elif nd.tag == "way":
				if "new_id" in nd.attrib:
					diffWays[int(nd.attrib["old_id"])] = map(int, (nd.attrib["new_id"], nd.attrib["new_version"]))
				else:
					diffWays[int(nd.attrib["old_id"])] = None
			elif nd.tag == "relation":
				if "new_id" in nd.attrib:
					diffRelations[int(nd.attrib["old_id"])] = map(int, (nd.attrib["new_id"], nd.attrib["new_version"]))
				else:
					diffRelations[int(nd.attrib["old_id"])] = None

		return diffNodes, diffWays, diffRelations

	def GetObject(self, objType, objId, getFull = False, getParentWays = False, getParentRelations = False):
		url = "{}/0.6/{}/{}".format(self.apiUrl, objType, objId)
		if getFull and objType == "node":
			raise RuntimeError ("Cannot get full data for a node")
		if getParentWays and objType != "node":
			raise RuntimeError ("Parent ways can only be retrieved for node")
		if int(getFull) + int(getParentWays) + int(getParentRelations) > 1:
			raise RuntimeError ("Only one option can be enabled")
		if getFull:
			url += "/full"
		if getParentWays:
			url += "/ways"
		if getParentRelations:
			url += "/relations"
		response = urlutil.Get(url,self.userpass)
		headerCode = urlutil.HeaderResponseCode(response[1])
		if headerCode == "HTTP/1.1 410 Gone": 
			raise GoneError()
		if headerCode != "HTTP/1.1 200 OK": 
			raise RuntimeError ("Error getting object data: "+ headerCode)
		return response[0]

