"""
author: Volker Lehmann
version: 0.1
last modified: 2017-08-24
"""

import os
from collections import OrderedDict
import re


class VCard:
    _properties = None
    _customProperties = None

    def __init__(self):
        """
        creates an instance of VCard class in v4.0, means that you can use
        VCard version v2.1 or v3.0 to initialize this class using static
        method "fromString", but as a result you will alway get a v4.0
        instance/representation
        """
        # store standard properties here
        self._properties = OrderedDict()
        # add properties, which are common across all known VCard verison
        self._properties["VERSION"] = "4.0"  # required in 2.1, 3.0, 4.0
        # required in 3.0, 4.0 // supported in 2.1
        self._properties["FN"] = None
        self._properties["UID"] = None  # supported in 2.1, 3.0, 4.0
        # required in 2.1, 3.0 // supported in 4.0
        self._properties["N"] = None
        self._properties["ORG"] = None  # supported in 2.1, 3.0, 4.0
        self._properties["TITLE"] = None  # supported in 2.1, 3.0, 4.0
        self._properties["TEL"] = []  # supported in 2.1, 3.0, 4.0
        self._properties["ADR"] = []  # supported in 2.1, 3.0, 4.0
        self._properties["EMAIL"] = []  # supported in 2.1, 3.0, 4.0
        self._properties["PHOTO"] = OrderedDict(
            [("MEDIATYPE", None), ("data", None)])  # supported in 2.1, 3.0, 4.0
        # supported in 2.1, 3.0, 4.0  //A timestamp for the last time the vCard was updated.
        self._properties["REV"] = None
        self._properties["URL"] = None  # supported in 2.1, 3.0, 4.0
        self._properties["NOTE"] = None  # supported in 2.1, 3.0, 4.0
        # store custom properties/extensions here
        self._customProperties = OrderedDict()

    @staticmethod
    def getKeyAndValueFromString(sData):
        sValue = ""
        # sData should be in format N:test;test
        # returns something like this ["N","test;test"]
        sTmp = sData.split(":")
        if (len(sTmp) > 1):  # make sure there is a value present
            sValue = sTmp[1]
        #
        sTmp2 = sTmp[0].split(";")  # returns something like this ["N"]
        sKey = sTmp2[0]
        return((sKey, sValue))

    @staticmethod
    def stripQuotes(sValue):
        """
        not in use yet, but put in here for future use
        """
        if ('"' in sValue) or ("'" in sValue):
            sValue = sValue.replace('"', '')
            sValue = sValue.replace("'", "")
        return sValue

    @staticmethod
    def getKeyAndValueQualifiersAsDict(sKey):
        """
        parse/split the key properties into a uniform format, because this seems to vary a lot
        """
        dictKeyProperties = OrderedDict(
            [("KEY", None), ("TYPE", []), ("PREF", None)])
        listKeySplit = sKey.split(";")
        for i in range(len(listKeySplit)):
            sValue = listKeySplit[i]
            # first in list should be the name of the key like N, EMAIL or ADR
            if (i == 0):
                sRegExWhichNeedsToMatch = "[A-Z]+"
                if (re.match(sRegExWhichNeedsToMatch, sValue)):
                    dictKeyProperties["KEY"] = sValue
                    continue
                else:
                    raise(ValueError("value '%s' does not match required regex '%s'" % (
                        sValue, sRegExWhichNeedsToMatch)))
            # check if we dealing with a TYPE
            if (sValue.startswith("TYPE")):
                # TYPE=work,voice
                sRegExWhichNeedsToMatch = "^[A-Z]+=[A-Za-z,]+$"
                if (re.match(sRegExWhichNeedsToMatch, sValue)):
                    tmpSplit = sValue.split("=")
                    # above regex allows "work,voice" and "WORK,VOICE",
                    # for consitency we'll continue with lowercase
                    tmpSplit[1] = tmpSplit[1].lower()
                    if ("," in tmpSplit[1]):  # multiple values (e.g. TYPE=work,voice)
                        tmpSplit = tmpSplit[1].split(",")
                        dictKeyProperties["TYPE"].extend(tmpSplit)
                    else:
                        # only one value after TYPE (e.g. TYPE=work)
                        dictKeyProperties["TYPE"].append(tmpSplit[1])
                    continue
                else:
                    raise(ValueError("value '%s' does not match required regex '%s'" % (
                        sValue, sRegExWhichNeedsToMatch)))
            # check if we dealing with a PREF
            if (sValue.startswith("PREF")):
                # e.g PREF or PREF=1 or PREF=2
                sRegExWhichNeedsToMatch = "^[A-Z]+[=0-9]*$"
                if (re.match(sRegExWhichNeedsToMatch, sValue)):
                    if ("=" in sValue):  # multiple values (e.g. PREF=1)
                        tmpSplit = sValue.split("=")
                        dictKeyProperties["PREF"] = int(tmpSplit[1])
                    else:
                        # no value after PREF (e.g. PREF)
                        # when no value was given, we set 1, by default
                        dictKeyProperties["PREF"] = 1
                    continue
                else:
                    raise(ValueError("value '%s' does not match required regex '%s'" % (
                        sValue, sRegExWhichNeedsToMatch)))
            # check if we dealing with a CHARSET
            if (sValue.startswith("CHARSET")):
                # e.g CHARSET=Windows-1252
                sRegExWhichNeedsToMatch = "^[A-Z]+=[A-Za-z\-0-9]+$"
                if (re.match(sRegExWhichNeedsToMatch, sValue)):
                    tmpSplit = sValue.split("=")
                    dictKeyProperties["CHARSET"] = tmpSplit[1]
                    continue
                else:
                    raise(ValueError("value '%s' does not match required regex '%s'" % (
                        sValue, sRegExWhichNeedsToMatch)))
            # check if we dealing with a ENCODING
            if (sValue.startswith("ENCODING")):
                # e.g ENCODING=QUOTED-PRINTABLE
                sRegExWhichNeedsToMatch = "^[A-Z]+=[A-Z\-]+$"
                if (re.match(sRegExWhichNeedsToMatch, sValue)):
                    tmpSplit = sValue.split("=")
                    dictKeyProperties["ENCODING"] = tmpSplit[1]
                    continue
                else:
                    raise(ValueError("value '%s' does not match required regex '%s'" % (
                        sValue, sRegExWhichNeedsToMatch)))
            # check if we dealing with a VALUE
            if (sValue.startswith("VALUE")):
                sRegExWhichNeedsToMatch = "^[A-Z]+=[a-z]+$"  # e.g VALUE=uri
                if (re.match(sRegExWhichNeedsToMatch, sValue)):
                    tmpSplit = sValue.split("=")
                    dictKeyProperties["VALUE"] = tmpSplit[1]
                    continue
                else:
                    raise(ValueError("value '%s' does not match required regex '%s'" % (
                        sValue, sRegExWhichNeedsToMatch)))
            # by default, if we do not recognize the value, raise an exception
            raise(ValueError("did not recognize this value '%s'" % sValue))
        return(dictKeyProperties)

    @staticmethod
    def _doStringReplacementsToUseStandardV4Parsing(sData):
        """
        replaces varios strings to standard v4 parsing possible
        so what is replaced:
          * linefeeds after '=0D=0A=' (which is used as linefeed within VCards e.g. NOTE)
          * v2.1 vcard strings, with a format compatible to VCard v4 format ...
          * LABEL, which is no longer supported as standalone in v4
        """
        # make sure we have the right line seperator
        sData = sData.replace("\r\n", "\n")
        #
        # "=0D=0A=", is a newline within a VCard property (e.g. NOTE)
        # we will not actually replace "=0D=0A=", but remove the following linefeed,
        # to get everything into the same line
        sData = sData.replace("=0D=0A=\n", "=0D=0A=")
        #
        # LABEL are no longer support as standalone in VCard v4 (only as part)
        sRegexLabel = "\nLABEL.*?\n"
        if (re.search(sRegexLabel, sData)):
            print("WARNING found 'LABEL' key word in VCard string, this will be removed, " +
                  "because it is no longer valid as a standalone in VCard v4.0")
            sData = re.sub(sRegexLabel, "\n", sData)
        #
        # v2.1 string replacements
        # sample EMAIL;PREF;INTERNET:jane_doe@abc.com -> EMAIL;TYPE=internet,pref:jane_doe@abc.com
        sData = re.sub(";PREF;INTERNET:", ";TYPE=internet,pref:", sData)
        #
        # EMAIL;INTERNET:jane_doe@abc.com  -> EMAIL;TYPE=internet:jane_doe@abc.com
        sData = re.sub(";INTERNET:", ";TYPE=internet:", sData)
        #
        # ADR;WORK;PREF:;;100 Waters Edge;Baytown;LA;30314;USA
        # -> ADR;TYPE=work,PREF:;;100 Waters Edge;Baytown;LA;30314;USA
        sData = re.sub("(ADR);(.*?)(;PREF)(:|;)",
                       "\g<1>;TYPE=\g<2>\g<3>\g<4>", sData)
        #
        sData = re.sub(";CELL;VOICE(:|;)", ";TYPE=cell,voice\g<1>", sData)
        sData = re.sub(";HOME;VOICE(:|;)", ";TYPE=home,voice\g<1>", sData)
        sData = re.sub(";WORK;VOICE(:|;)", ";TYPE=work,voice\g<1>", sData)
        sData = re.sub(";PAGER;VOICE(:|;)", ";TYPE=pager,voice\g<1>", sData)
        sData = re.sub(";HOME(:|;)", ";TYPE=home\g<1>", sData)
        #
        sData = re.sub(";VALUE=URI;TYPE=GIF(:|;)",
                       ";MEDIATYPE=image/gif\g<1>", sData)  # PHOTO
        sData = re.sub(";PHOTO;GIF(:|;)",
                       ";MEDIATYPE=image/gif\g<1>", sData)  # PHOTO
        #
        return(sData)

    @staticmethod
    def _getFileContent(sVCardFilePath):
        sContent = ""
        # check if file and accessable
        if (os.path.exists(sVCardFilePath)):
            if (os.path.isfile(sVCardFilePath)):
                pass  # path is acessable and points to file, all good
            else:
                raise(ValueError("a file path pointing to a VCard file was expected, but a folder path was given '%s'" % sVCardFilePath))
        else:
            raise(Exception("given file path is not accessable '%s'" % sVCardFilePath))
        # load bytes of file and find the right encoding (ANSI, LATIN1 or UTF8)
        with open(sVCardFilePath, "rb") as fhVCardFile:
            fileData = fhVCardFile.read()
            try:
                # check if file content is UTF8 (default format for VCard v4.0)
                sContent = fileData.decode('utf-8')
            except UnicodeDecodeError:
                # maybe it is 'LATIN1'
                try:
                    sContent = fileData.decode('latin1')
                except UnicodeDecodeError as ex:
                    # maybe it is 'ASCII' (default format for VCard v2.1)
                    try:
                        sContent = fileData.decode('ascii')
                    except UnicodeDecodeError as ex:
                        print(
                            "could not decode VCard file, neither 'UTF8', 'LATIN1' nor 'ASCII' worked")
                        raise(ex)
                    # end try ascii
                # end try latin1
            # end try utf8
        return(sContent)

    @staticmethod
    def fromString(sData):
        # do some string replacements to use the standard v4 parsing methods
        sData = VCard._doStringReplacementsToUseStandardV4Parsing(sData)
        # split the data into lines
        listData = sData.split("\n")
        # create a new VCard instance
        objVCard = VCard()
        # parse the given data by line and assign the values to our new VCard instance
        for sLine in listData:
            # skip these two lines
            sLineStrippedUpper = sLine.strip().upper()
            if (sLineStrippedUpper == "BEGIN:VCARD") or (sLineStrippedUpper == "END:VCARD"):
                continue
            # check for known keys
            (sKey, sValue) = VCard.getKeyAndValueFromString(sLine)
            sKey = sKey.strip().upper()
            if sKey == "VERSION":
                # version of the VCard object will be v4, regardless what the original VCard string was
                continue
            # generic approach
            try:
                if (objVCard.hasProperty(sKey)):
                    refMethod = eval("objVCard.set%s" % sKey)
                    refMethod(sLine)
                else:
                    if (sKey.startswith("X")):
                        sTmp = sLine.split(":", 1)
                        objVCard.addCustomProperty(sTmp[0], sTmp[1])
                    else:
                        print(
                            "WARNING found unknown property, which does not start with an 'X' // '%s', this data will be ignored" % sKey)
                        print("VERBOSE data to be ignored '%s'" % sLine)
                #
            except Exception as ex:
                print("ERROR could no add this line '%s' to VCard object" % sLine)
                print(str(ex))
                raise(ex)
            #
        return(objVCard)

    @staticmethod
    def fromFile(sVCardFilePath):
        listOfVCards = []
        #
        # get file content
        sContent = VCard._getFileContent(sVCardFilePath)
        # find VCards in file
        matches = re.findall("BEGIN:VCARD.*?END:VCARD", sContent, re.DOTALL)
        for match in matches:
            matchesVersion = re.findall("VERSION:([2-4]\.[0-1])", str(match))
            if len(matchesVersion) != 1:
                raise(Exception("found more than one version string working in file '%s' and on VCard data '%s'" % (
                    sFilePath, sContent)))
            if ((matchesVersion[0] == "2.1") or (matchesVersion[0] == "3.0") or (matchesVersion[0] == "4.0")):
                # remove print("\n\nfound version %s VCard data" % matchesVersion[0])
                objVCard = VCard.fromString(str(match))
                listOfVCards.append(objVCard)
            else:
                print("unknown version, not implemented, found VCard version '%s' in file '%s'" % (
                    matchesVersion[0], sFilePath))
        return(listOfVCards)

    def hasProperty(self, sPropertyName):
        if sPropertyName in self._properties:
            return True
        else:
            return False

    def hasCustomProperty(self, sPropertyName):
        if sPropertyName in self._customProperties:
            return True
        else:
            return False

    def addCustomProperty(self, sPropertyName, sPropertyValue):
        self._customProperties[sPropertyName] = sPropertyValue

    def getCustomProperty(self, sPropertyName):
        return self._customProperties[sPropertyName]

    @property
    def version(self):
        return self._properties["VERSION"]

    @property
    def surname(self):
        return self._properties["N"]["surname"]

    @surname.setter
    def surname(self, value):
        self._properties["N"]["surname"] = value

    @property
    def givenName(self):
        return self._properties["N"]["givenName"]

    @givenName.setter
    def givenName(self, value):
        self._properties["N"]["givenName"] = value

    @property
    def additonalNames(self):
        return self._properties["N"]["additonalNames"]

    @additonalNames.setter
    def additonalNames(self, value):
        self._properties["N"]["additonalNames"] = value

    @property
    def honorificPrefixes(self):
        return self._properties["N"]["honorificPrefixes"]

    @honorificPrefixes.setter
    def honorificPrefixes(self, value):
        self._properties["N"]["honorificPrefixes"] = value

    @property
    def honorificSuffixes(self):
        return self._properties["N"]["honorificSuffixes"]

    @honorificSuffixes.setter
    def honorificSuffixes(self, value):
        self._properties["N"]["honorificSuffixes"] = value

    @property
    def VERSION(self):
        return("VERSION:%s" % (self.version))

    @property
    def N(self):
        if self._properties["N"] is None:
            return("")
        else:
            return("N:%s;%s;%s;%s;%s" % (self.surname, self.givenName, self.additonalNames, self.honorificPrefixes, self.honorificSuffixes))

    def setN(self, value):
        """
        sample:
        N:Gump;Forrest;;Mr.
        N;LANGUAGE=de:Gump;Forrest
        """
        tmpSplit = value.split(":")
        if (len(tmpSplit) == 2) and (tmpSplit[0].startswith("N")):
            self._properties["N"] = OrderedDict([("surname", ""), ("givenName", ""), (
                "additonalNames", ""), ("honorificPrefixes", ""), ("honorificSuffixes", "")])
            tmpSplit2 = tmpSplit[1].split(";")
            listKeysOfN = list(self._properties["N"].keys())
            for i in range(0, len(tmpSplit2)):
                self._properties["N"][listKeysOfN[i]] = tmpSplit2[i]
        else:
            raise(ValueError(
                "could not parse string for 'N', tried to parse this '%s'" % (value)))

    @property
    def formattedNameString(self):
        return self._properties["FN"]

    @property
    def FN(self):
        return("FN:%s" % (self.formattedNameString))

    def setFN(self, value):
        tmpSplit = value.split(":")
        if (len(tmpSplit) == 2) and (tmpSplit[0].startswith("FN")):
            self._properties["FN"] = tmpSplit[1]
        else:
            raise(ValueError(
                "could not parse string for 'FN', tried to parse this '%s'" % (value)))

    @property
    def organisation(self):
        return self._properties["ORG"]

    @property
    def ORG(self):
        return("ORG:%s" % (self.organisation))

    def setORG(self, value):
        tmpSplit = value.split(":")
        if (len(tmpSplit) == 2) and (tmpSplit[0].startswith("ORG")):
            self._properties["ORG"] = tmpSplit[1]
        else:
            raise(ValueError(
                "could not parse string for 'ORG', tried to parse this '%s'" % (value)))

    @property
    def title(self):
        return self._properties["TITLE"]

    @property
    def TITLE(self):
        return("TITLE:%s" % (self.title))

    def setTITLE(self, value):
        tmpSplit = value.split(":")
        if (len(tmpSplit) == 2) and (tmpSplit[0].startswith("TITLE")):
            self._properties["TITLE"] = tmpSplit[1]
        else:
            raise(ValueError(
                "could not parse string for 'TITLE', tried to parse this '%s'" % (value)))

    @property
    def EMAIL(self):
        sStr = ""
        for dictMail in self._properties["EMAIL"]:
            # if we have multiple email addresses use a line break as seperator
            if (sStr != ""):
                sStr += "\n"
            sStr += "EMAIL"
            if dictMail["type"] is not None:
                sStr += ";TYPE=%s" % dictMail["type"]
            if dictMail["pref"] is not None:
                sStr += ",pref"
            # add mail address
            sStr += (":" + dictMail["address"])
        return(sStr)

    def setEMAIL(self, value):
        """
        sample from RFC 2426
        EMAIL;TYPE=internet:jqpublic@xyz.dom1.com
        EMAIL;TYPE=internet:jdoe@isp.net
        EMAIL;TYPE=internet,pref:jane_doe@abc.com
        """
        # split into mail string
        dictMail = OrderedDict(
            [("type", None), ("pref", None), ("address", "")])
        # should result in ["EMAIL;TYPE=internet,pref", "jane_doe@abc.com"]
        tmpSplit = value.split(":")
        if (len(tmpSplit) == 2) and (tmpSplit[0].startswith("EMAIL")):
            # should result in ["EMAIL", "TYPE=internet,pref"]
            tmpSplit2 = tmpSplit[0].split(";")
            if ((len(tmpSplit2) == 2) and (tmpSplit2[1].startswith("TYPE"))):
                # should result in ["TYPE=internet", "pref"]
                tmpSplit3 = tmpSplit2[1].split(",")
                # check if pref is specified
                if (len(tmpSplit3) == 2):
                    dictMail["pref"] = True
                # get type value
                # should result in ["TYPE", "internet"]
                tmpSplit4 = tmpSplit3[0].split("=")
                dictMail["type"] = tmpSplit4[1]
            # set email address
            dictMail["address"] = tmpSplit[1]
        else:
            raise(ValueError(
                "could not parse string for 'EMAIL', tried to parse this '%s'" % (value)))
        #
        self._properties["EMAIL"].append(dictMail)

    @property
    def TEL(self):
        sStr = ""
        for dictTel in self._properties["TEL"]:
            # if we have multiple tel use a line break as seperator
            if (sStr != ""):
                sStr += "\n"
            sStr += "TEL"
            if dictTel["TYPE"] is not None:
                sStr += ";TYPE=%s" % ",".join(dictTel["TYPE"])
            if dictTel["PREF"] is not None:
                sStr += ";PREF=%d" % dictTel["PREF"]
            if dictTel["VALUE"] is not None:
                sStr += ";VALUE=%s" % dictTel["VALUE"]
            # add tel data
            sStr += (":" + dictTel["data"])
        return(sStr)

    def setTEL(self, value):
        """
        sample from RFC 6350
        TEL;VALUE=uri;TYPE=work,voice;PREF=1:tel:+1-418-656-9254;ext=102  #
        """
        sExpectedKeyValue = "TEL"
        # parse key part
        dictTel = OrderedDict(
            [("TYPE", None), ("PREF", None), ("VALUE", None), ("data", None)])
        # should result in ("TEL;VALUE=uri;TYPE=work,voice;PREF=1", "tel:+1-418-656-9254;ext=102")
        (sKey, sValue) = value.split(":", 1)
        dictKeyQualifier = VCard.getKeyAndValueQualifiersAsDict(sKey)
        for key in dictKeyQualifier.keys():
            if (key == "KEY"):
                if (dictKeyQualifier["KEY"] != sExpectedKeyValue):
                    raise(ValueError("this should not happen. KEY is '%s', but should be '%s' (tried to parse this '%s'" % (
                        dictKeyQualifier["KEY"], sExpectedKeyValue, value)))
            else:
                dictTel[key] = dictKeyQualifier[key]
        #
        # parse value part
        dictTel["data"] = sValue
        #
        self._properties["TEL"].append(dictTel)

    @property
    def ADR(self):
        sStr = ""
        for dictAdrEntry in self._properties["ADR"]:
            # if we have multiple email addresses use a line break as seperator
            if (sStr != ""):
                sStr += "\n"
            sStr += "ADR"
            if dictAdrEntry["TYPE"] is not None:
                sStr += ";TYPE=%s" % dictAdrEntry["TYPE"]
            if dictAdrEntry["PREF"] is not None:
                sStr += ",pref"
            # add address
            sStr += (":" + ";".join(dictAdrEntry["address"].values()))
        return(sStr)

    def setADR(self, value):
        """
        sample from RFC 6350
        ADR;TYPE=work,PREF:;Suite D2-630;2875 Laurier;Quebec;QC;G1V 2M2;Canada
        """
        # split into mail string
        dictAdrEntry = OrderedDict(
            [("TYPE", None), ("PREF", None), ("address", None)])
        dictAdrEntry["address"] = OrderedDict([("postOfficeBox", ""), ("extendedAddress", ""), (
            "streetAddress", ""), ("locality", ""), ("region", ""), ("postalCode", ""), ("countryName", "")])
        # should result in ["ADR;TYPE=work,PREF", ";Suite D2-630;2875 Laurier;Quebec;QC;G1V 2M2;Canada"]
        tmpSplit = value.split(":")
        if (len(tmpSplit) == 2) and (tmpSplit[0].startswith("ADR")):
            # should result in ["ADR", "TYPE=work,PREF"]
            tmpSplit2 = tmpSplit[0].split(";")
            if ((len(tmpSplit2) == 2) and (tmpSplit2[1].startswith("TYPE"))):
                # should result in ["TYPE=internet", "PREF"]
                tmpSplit3 = tmpSplit2[1].split(",")
                # check if pref is specified
                if (len(tmpSplit3) == 2):
                    dictAdrEntry["PREF"] = True
                # get type value
                # should result in ["TYPE", "internet"]
                tmpSplit4 = tmpSplit3[0].split("=")
                dictAdrEntry["TYPE"] = tmpSplit4[1].lower()
            # split address
            tmpAddress = tmpSplit[1].split(";")
            # should result in ["","Suite D2-630", "2875 Laurier" ,"Quebec", "QC", "G1V 2M2", "Canada"]
            tmpAddress = tmpSplit[1].split(";")
            listKeysOfAddress = list(dictAdrEntry["address"].keys())
            for i in range(0, len(tmpAddress)):
                dictAdrEntry["address"][listKeysOfAddress[i]] = tmpAddress[i]
        else:
            raise(ValueError(
                "could not parse string for 'ADR', tried to parse this '%s'" % (value)))
        #
        self._properties["ADR"].append(dictAdrEntry)

    @property
    def PHOTO(self):
        sStr = ""
        if self._properties["PHOTO"]["data"] is not None:
            sStr += "PHOTO"
            if self._properties["PHOTO"]["MEDIATYPE"] is not None:
                sStr += ";MEDIATYPE=%s" % (self._properties["PHOTO"]["MEDIATYPE"])
            # add data
            sStr += (":" + self._properties["PHOTO"]["data"])
        return(sStr)

    def setPHOTO(self, value):
        """
        example PHOTO;MEDIATYPE=image/gif:http://www.example.com/dir_photos/my_photo.gif
        """
        tmpSplit = value.split(
            ":", 1)  # should result in ["PHOTO;MEDIATYPE=image/gif", "http://www.example.com/dir_photos/my_photo.gif"]
        if (len(tmpSplit) == 2) and (tmpSplit[0].startswith("PHOTO")):
            # should result in ["PHOTO", "MEDIATYPE=image/gif"]
            tmpSplit2 = tmpSplit[0].split(";")
            if ((len(tmpSplit2) == 2) and (tmpSplit2[1].startswith("MEDIATYPE"))):
                self._properties["PHOTO"]["MEDIATYPE"] = tmpSplit2[1].split("=")[1]
            self._properties["PHOTO"]["data"] = tmpSplit[1]
        else:
            raise(ValueError("could not parse string for 'PHOTO', tried to parse this '%s'" % (value)))

    @property
    def REV(self):
        return("REV:%s" % (self._properties["REV"]))

    def setREV(self, value):
        tmpSplit = value.split(":", 1)
        if (len(tmpSplit) == 2) and (tmpSplit[0].startswith("REV")):
            self._properties["REV"] = tmpSplit[1]
        else:
            raise(ValueError("could not parse string for 'REV', tried to parse this '%s'" % (value)))

    @property
    def UID(self):
        if self._properties["UID"] is None:
            return("")
        else:
            return("UID:%s" % (self._properties["UID"]))

    def setUID(self, value):
        tmpSplit = value.split(":", 1)
        if (len(tmpSplit) == 2) and (tmpSplit[0].startswith("UID")):
            self._properties["UID"] = tmpSplit[1]
        else:
            raise(ValueError("could not parse string for 'UID', tried to parse this '%s'" % (value)))

    @property
    def NOTE(self):
        if self._properties["NOTE"] is None:
            return("")
        else:
            return("NOTE:%s" % (self._properties["NOTE"]))

    def setNOTE(self, value):
        tmpSplit = value.split(":", 1)
        if (len(tmpSplit) == 2) and (tmpSplit[0].startswith("NOTE")):
            self._properties["NOTE"] = tmpSplit[1]
        else:
            raise(ValueError("could not parse string for 'NOTE', tried to parse this '%s'" % (value)))

    @property
    def URL(self):
        if self._properties["URL"] is None:
            return("")
        else:
            return("URL:%s" % (self._properties["URL"]))

    def setURL(self, value):
        tmpSplit = value.split(":", 1)
        if (len(tmpSplit) == 2) and (tmpSplit[0].startswith("URL")):
            self._properties["URL"] = tmpSplit[1]
        else:
            raise(ValueError("could not parse string for 'URL', tried to parse this '%s'" % (value)))

    def prettyPrint(self, bIncludeCustomProperties=True):
        sVCard = ""
        # begin tag
        sVCard += "BEGIN:VCARD"
        # add standard properties
        for sProperty in self._properties:
            sLine = eval("self.%s" % sProperty)
            if (len(sLine) > 0):
                sVCard += "\n" + sLine
        # include custom properties /properties starting with "X"
        if (bIncludeCustomProperties is True):
            for sCustomProperty in self._customProperties:
                sVCard += "\n%s:%s" % (sCustomProperty, self.getCustomProperty(sCustomProperty))
        # end tag
        sVCard += "\nEND:VCARD\n"
        return(sVCard)

    def __str__(self):
        return("VCard:v%s //FN:%s //N:%s" % (self.version, self.FN, self.N))


if __name__ == "__main__":
    # init argument parser
    import argparse
    objArgumentParser = argparse.ArgumentParser(
        description='SYNTAX: vcard.py -i inputFolder -o outputFolder')
    objArgumentParser.add_argument("-i", action="store", type=str, dest="inputFolder",
                                   default="", required=True, help="folder to look for .vcf files")
    objArgumentParser.add_argument("-o", action="store", type=str, dest="outputFolder", default="",
                                   required=False, help="if specified, exported .vcf files will be written here")
    objArgumentParser.add_argument("-export", action="store_true", dest="bExportVCards", required=False,
                                   help="if specified, parsed VCards will be exported, with new extension 'v4.vcf'")
    argsParsed = objArgumentParser.parse_args()
    #
    # set vars
    sInputFolder = argsParsed.inputFolder
    sExportFileExtension = ".v4.vcf"
    bExportVCards = argsParsed.bExportVCards
    # if no outputFolder is specified, we will use the inputFolder to export the data, if -export was specified
    if (len(argsParsed.outputFolder) > 0):
        sExportFolder = argsParsed.outputFolder
    else:
        sExportFolder = argsParsed.inputFolder
    #
    # check that input folder is accessable
    if os.path.exists(sInputFolder) is False:
        raise(Exception(
            "could not access specified input folder '%s', please verify" % sInputFolder))
    #
    # get all files
    setOfFilesToLoad = set()
    for root, directories, filenames in os.walk(sInputFolder):
        for filename in filenames:
            if (filename.endswith(sExportFileExtension) is False):
                setOfFilesToLoad.add(os.path.join(root, filename))
    #
    # load VCard files and try to parse them
    for sFilePath in sorted(setOfFilesToLoad):
        sVCardStringsForExport = ""
        print("about to load '%s'" % sFilePath)
        listVCards = VCard.fromFile(sFilePath)
        for objVCard in listVCards:
            print("\n###############parsed and pretty printed##############")
            sVCard = objVCard.prettyPrint(bIncludeCustomProperties=False)
            print(sVCard)
            sVCardStringsForExport += sVCard
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        # export the parsed and pretty printed data if needed
        if bExportVCards:
            sOutFile = sFilePath.replace(".vcf", sExportFileExtension)
            sOutFile = sOutFile.replace(sInputFolder, sExportFolder)
            with (open(sOutFile, "wb")) as fhOut:
                fhOut.write(sVCardStringsForExport.encode("utf8"))
            print("file '%s' was written" % sOutFile)
    # end for sFilePath
