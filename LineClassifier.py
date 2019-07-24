#!/usr/bin/python
#-*-coding:utf-8-*-

import re
import ConfigParser
from optparse import OptionParser
g_szVersion = "1.0.0"

g_OptParser = OptionParser(version="%%prog %s" % (g_szVersion))

class CSectionObject():
  def printResult(self):
    for curItem in self.m_lst_result:
      print curItem
  def addResult(self, szLine):
    self.m_lst_result.append(szLine)
  def search(self, szLine):
    if (self.m_CompiledRegex == None):
      return 0
    if ( self.mv_mstype == 'm' ):
      if (self.m_CompiledRegex.match(szLine) != None):
        return 1
    else:
      if (self.m_CompiledRegex.search(szLine) != None):
        return 1
    return 0
  def getINI_Value(self, szKeyName, szDefault = None):
    szRet=szDefault
    try:
      szRet=self.m_ini_cfg.get(self.m_szSectionName, szKeyName)
      if ( len(szRet) == 0 ):
        szRet=szDefault
    except:
      pass
    return szRet
  def __init__(self, _ini_cfg, szCurSection):
    self.m_lst_result=list()
    self.m_szSectionName = szCurSection
    self.m_ini_cfg = _ini_cfg
    self.mv_regex=self.getINI_Value("regex", None)
    self.mv_case_ignore=self.getINI_Value("case_ignore", "0")
    self.mv_use=self.getINI_Value("use", "0")
    self.mv_parent=self.getINI_Value("parent", None)
    self.mv_alias=self.getINI_Value("alias", None)
    self.mv_mstype=self.getINI_Value("mstype", 's') # search
    self.m_reOpt = 0
    if ( self.mv_case_ignore ):
      self.m_reOpt |= re.IGNORECASE
    if ( self.mv_use == "0" ):
      self.m_CompiledRegex = None
    else:
      self.m_CompiledRegex = re.compile(self.mv_regex, self.m_reOpt)

class CLineFormatClassifier():
  def __init__(self):
    self.m_dictSysVariable = dict()
    self.m_ListSysVariable = list() # sequential running
  def printResult(self):
    for curSecName in self.m_ListSysVariable:
       szPrintSecName=curSecName
       if ( self.m_dictSysVariable[curSecName].mv_alias != None):
         szPrintSecName=self.m_dictSysVariable[curSecName].mv_alias
       print "%s" % szPrintSecName
       self.m_dictSysVariable[curSecName].printResult()
  def doIt(self, szLine):
    for curSecName in self.m_ListSysVariable:
       if ( curSecName == "default" ):
         continue
       curObj = self.m_dictSysVariable[curSecName]
       isMatch=0
       while True:
         if ( curObj == None):
           break
         isMatch = curObj.search(szLine)
         if ( isMatch == 0 ):
           break
         else:
           if ( curObj.mv_parent != None ):
             curObj=self.m_dictSysVariable[curObj.mv_parent]
           else:
             curObj=None
       if ( isMatch > 0 ):
         self.m_dictSysVariable[curSecName].addResult(szLine)
         return
    if ( self.m_dictSysVariable["default"].search(szLine) ):
      self.m_dictSysVariable["default"].addResult(szLine)
  def loadConfig(self, argConfig):
    self.m_ini_cfg = ConfigParser.ConfigParser()
    self.m_ini_cfg.optionxform = str
    self.m_ini_cfg.read(argConfig)
    for szCurSection in self.m_ini_cfg.sections():
      self.m_dictSysVariable[szCurSection] = CSectionObject(self.m_ini_cfg, szCurSection)
      self.m_ListSysVariable.append(szCurSection)

def main():
  requiredOpts = "filename cfgname".split()
  g_OptParser.add_option("-c", "--cfgname", dest="cfgname", \
    help="Config INI filename", metavar="FILE")
  g_OptParser.add_option("-f", "--filename", dest="filename", \
    help="Config INI filename", metavar="FILE")
  (options, args) = g_OptParser.parse_args()
  for szOptValName in requiredOpts:
    if options.__dict__[szOptValName] is None:
      g_OptParser.error("parameter %s required" % szOptValName)
  objLFC = CLineFormatClassifier()
  objLFC.loadConfig(options.cfgname)
  fp_File = open(options.filename, "r")
  for curLine in fp_File.read().split("\n"):
    objLFC.doIt(curLine)
  fp_File.close()
  objLFC.printResult()

if __name__ == "__main__":
  main()
