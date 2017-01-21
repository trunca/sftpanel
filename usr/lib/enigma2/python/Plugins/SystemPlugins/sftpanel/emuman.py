# by 2boom 2011-2015 4bob@ua.fm 
from Components.config import config, getConfigListEntry, ConfigText, ConfigPassword, ConfigSelection, ConfigSubsection, ConfigYesNo,   config, configfile
from Components.ConfigList import ConfigListScreen
from Components.ScrollLabel import ScrollLabel
from Components.Sources.StaticText import StaticText
from Components.ActionMap import ActionMap, NumberActionMap
from Screens.PluginBrowser import PluginBrowser
from Screens.MessageBox import MessageBox
from Components.MenuList import MenuList
from Components.Sources.List import List
from Tools.LoadPixmap import LoadPixmap
from Plugins.Plugin import PluginDescriptor
from Components.Console import Console as iConsole
from Screens.Screen import Screen
from Components.Label import Label
from enigma import eTimer
from Components.Language import language
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from os import environ, listdir
import time
import os
import gettext
import tools
import sys

lang = language.getLanguage()
environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("sftpanel", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/sftpanel/locale"))

def _(txt):
	t = gettext.dgettext("sftpanel", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

def Check_cccam():
    	found = False
    	for x in listdir('/usr/bin'):
        	if x.find('CCcam') > -1:
            		found = True
            		break

    	return found

def Check_oscam():
    	found = False
    	for x in listdir('/usr/bin'):
        	if x.find('oscam') > -1:
            		found = True
           		break

    	return found

def logging(line):
	log_file = open('/tmp/sftpanel.log', 'a')
	log_file.write(line)
	log_file.close()
####################################################################
config.plugins.sftpanel.activeserver = ConfigText(default = "NotSelected")
config.plugins.sftpanel.activeconf = ConfigText(default = "NotSelected")
config.plugins.sftpanel.activeemu = ConfigText(default = "NotSelected")
config.plugins.sftpanel.addbiss = ConfigSelection(default = "0", choices = [
		("0", _("No")),
		("1", _("Yes")),
		])
config.plugins.sftpanel.path = ConfigSelection(default = "/usr/keys/", choices = [
		("/usr/keys/", "/usr/keys/"),
		("/etc/keys/", "/etc/keys/"),
		("/etc/tuxbox/config/", "/etc/tuxbox/config/"),
		("/etc/tuxbox/config/oscam-stable/", "/etc/tuxbox/config/oscam-stable/"),
		])
config.plugins.sftpanel.keyname = ConfigSelection(default = "SoftCam.Key", choices = [
		("SoftCam.Key", "SoftCam.Key"),
		("oscam.keys", "oscam.keys"),
		("oscam.biss", "oscam.biss"),
		])
config.plugins.sftpanel.softcamserver = ConfigText(default="http://softcam.esy.es/softcam/SoftCam.Key", visible_width = 200, fixed_size = False)
config.plugins.usw = ConfigSubsection()
config.plugins.usw.activeconf = ConfigText(default = "")
config.plugins.usw.configpath = ConfigText(default = "")
config.plugins.usw.emu = ConfigText(default = "")
config.plugins.usw.configfile = ConfigText(default = "")
config.plugins.usw.configext = ConfigText(default = "")

config.plugins.uswmgcamd = ConfigSubsection()
config.plugins.uswmgcamd.active = ConfigYesNo(default = False)
config.plugins.uswmgcamd.activeconf = ConfigText(default = "NotSelected")
config.plugins.uswmgcamd.configpath = ConfigText(default="/usr/keys", visible_width = 200, fixed_size = False)
config.plugins.uswmgcamd.configfile = ConfigText(default="newcamd.list", visible_width = 200, fixed_size = False)
config.plugins.uswmgcamd.configext = ConfigText(default="nl", visible_width = 100, fixed_size = False)

config.plugins.uswwicardd = ConfigSubsection()
config.plugins.uswwicardd.active = ConfigYesNo(default = False)
config.plugins.uswwicardd.activeconf = ConfigText(default = "NotSelected")
config.plugins.uswwicardd.configpath = ConfigText(default="/etc/tuxbox/config", visible_width = 200, fixed_size = False)
config.plugins.uswwicardd.configfile = ConfigText(default="wicardd.conf", visible_width = 200, fixed_size = False)
config.plugins.uswwicardd.configext = ConfigText(default="wc", visible_width = 100, fixed_size = False)

config.plugins.uswoscam = ConfigSubsection()
config.plugins.uswoscam.active = ConfigYesNo(default = False)
config.plugins.uswoscam.activeconf = ConfigText(default = "NotSelected")
config.plugins.uswoscam.configpath = ConfigText(default="/etc/tuxbox/config/oscam-stable", visible_width = 200, fixed_size = False)
config.plugins.uswoscam.configfile = ConfigText(default="oscam.conf", visible_width = 200, fixed_size = False)
config.plugins.uswoscam.configext = ConfigText(default="os", visible_width = 100, fixed_size = False)

config.plugins.uswcccam = ConfigSubsection()
config.plugins.uswcccam.active = ConfigYesNo(default = False)
config.plugins.uswcccam.activeconf = ConfigText(default = "NotSelected")
config.plugins.uswcccam.configpath = ConfigText(default="/etc/", visible_width = 200, fixed_size = False)
config.plugins.uswcccam.configfile = ConfigText(default="CCcam.cfg", visible_width = 200, fixed_size = False)
config.plugins.uswcccam.configext = ConfigText(default="cc", visible_width = 100, fixed_size = False)
######################################################################################
def ecm_view():
	list = ''
	port_flag = 0
	if fileExists("/tmp/ecm.info"):
		try:
			ecmfiles = open('/tmp/ecm.info', 'r')
			for line in ecmfiles:
				if 'port:' in line: 
					port_flag  = 1
				if 'caid:' in line or 'provider:' in line or 'provid:' in line or 'pid:' in line or 'hops:' in line or 'system:' in line or 'address:' in line or 'using:' in line or 'ecm time:' in line:
					line = line.replace(' ','').replace(':',': ')
				if 'from:' in line or 'protocol:' in line or 'caid:' in line or 'pid:' in line or 'reader:' in line or 'hops:' in line or 'system:' in line or 'Service:' in line or 'CAID:' in line or 'Provider:' in line:
					line = line.strip('\n') + '  '
				if 'Signature' in line:
					line = ""
				if '=' in line:
					line = line.lstrip('=').replace('======', "").replace('\n', "").rstrip() + ', '
				if 'ecmtime:' in line:
					line = line.replace('ecmtime:', 'ecm time:')
				if 'response time:' in line:
					line = line.replace('response time:', 'ecm time:').replace('decoded by', 'by')
				if not line.startswith('\n'): 
					if 'protocol:' in line and port_flag == 0:
						line = '\n' + line
					if 'pkey:' in line:
						line = '\n' + line + '\n'
					list += line
			ecmfiles.close()
			return list
		except:
			return ''
	return ''
######################################################################################
class emuSel5(Screen):
	skin = """
<screen name="emuSel5" position="center,225" size="1300,720" title="Select SoftCam or CardServer">
  <ePixmap pixmap="MX_HQ7/menu/bb.png" position="18,638" size="1264,74" zPosition="-1" alphatest="on"/>
<ePixmap pixmap="MX_HQ7/menu/mainsoftcam.png" position="945,160" size="250,250" zPosition="-1" alphatest="on"/>
<ePixmap pixmap="MX_HQ7/menu/exit.png" position="1212,650" size="48,48" alphatest="blend"/>
<ePixmap pixmap="MX_HQ7/buttons/green48x48.png" position="330,650" size="48,48" alphatest="blend"/>
<ePixmap pixmap="MX_HQ7/buttons/yellow48x48.png" position="630,650" size="48,48" alphatest="blend"/>
<ePixmap pixmap="MX_HQ7/buttons/blue48x48.png" position="930,650" size="48,48" alphatest="blend"/>
<ePixmap pixmap="MX_HQ7/buttons/red48x48.png" position="30,650" size="48,48" alphatest="blend"/>
<widget source="key_red" render="Label" position="90,640" size="240,70" zPosition="1" font="Regular;32" halign="left" valign="center" foregroundColor="button" backgroundColor="bgkey" transparent="1"/>
<widget source="key_green" render="Label" position="390,640" size="250,70" zPosition="1" font="Regular;28" halign="left" valign="center" foregroundColor="button" backgroundColor="bgkey" transparent="1"/>
<widget source="key_yellow" render="Label" position="690,640" size="240,70" zPosition="1" font="Regular;28" halign="left" valign="center" foregroundColor="button" backgroundColor="bgkey" transparent="1"/>
<widget source="key_blue" render="Label" position="990,640" size="240,70" zPosition="1" font="Regular;28" halign="left" valign="center" foregroundColor="button" backgroundColor="bgkey" transparent="1"/>
 <widget name="text" position="220,400" size="600,205" font="Regular;24" halign="center" noWrap="1" />
<widget source="menu" render="Listbox" enableWrapAround="1" position="20,20" size="820,605" zPosition="1" foregroundColor="button" backgroundColor="bgbutton" backgroundColorSelected="selbutton" backgroundPixmap="MX_HQ7/menu/bg820x55.png" selectionPixmap="MX_HQ7/menu/sel820x55.png" scrollbarMode="showNever" transparent="1">
<convert type="TemplatedMultiContent">
{"template": [ MultiContentEntryText(pos = (70, 9), size = (710, 35), flags = RT_HALIGN_LEFT, text =0),
MultiContentEntryPixmapAlphaTest(pos = (10, 7), size = (40, 40), png = 2), 
],
"fonts": [gFont("Regular",34)],
"itemHeight":55
}
</convert>
</widget>
<widget source="global.CurrentTime" render="Label" position="840,50" size="460,70" font="Regular;65" halign="center" foregroundColor="info" backgroundColor="bgmain" transparent="1">
<convert type="ClockToText">Default</convert>
</widget>
<widget source="session.CurrentService" render="Label" position="850,480" size="440,100" font="Regular;38" halign="center" foregroundColor="info" backgroundColor="bgmain" transparent="1">
<convert type="ServiceName">Name</convert>
</widget>
</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.setTitle(_("Select SoftCam or CardServer: - %s") % config.plugins.sftpanel.activeemu.value)
		self.session = session
		self.iConsole = iConsole()
		self.current_emu = ''
		self.emutype = ''
		self.list = []
		self.indexpos = None
		self["menu"] = List(self.list)
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
			{
				"cancel": self.cancel,
				"ok": self.ok,
				"green": self.ok,
				"red": self.emuStopOperation,
				"yellow": self.emuRestartOperation,
				"blue": self.switcher,
			},-1)
		self.list = [ ]
		self["key_red"] = Label(_("Stop"))
		self["key_green"] = Label(_("Start"))
		self["key_yellow"] = Label(_("ReStart"))
		self["key_blue"] = Label(_("Switcher"))
		self["text"] = ScrollLabel("")
		self["inmemory"] = StaticText()
		self.listecm()
		self.Timer = eTimer()
		self.Timer.callback.append(self.listecm)
		self.Timer.start(1000*4, False)
		self.selemulist()
		
	def selemulist(self):
		self.list = []
		typeemu = ' '
		camdlist = os.listdir("/etc/init.d/")
		for line in camdlist:
			if '.None' not in line and '.none' not in line:
				if line.split(".")[0] == 'softcam':
					typeemu = 'softcam'
					if self.emuversion(line) == self.emuversion('softcam'):
						softpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/sftpanel/images/%s" % 'emuact.png'))
					else:
						softpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/sftpanel/images/%s" % 'emumini.png'))
				elif line.split(".")[0] == 'cardserver':
					typeemu = 'cardserver'
					if self.emuversion(line) == self.emuversion('cardserver'):
						softpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/sftpanel/images/%s" % 'cardact.png'))
					else:
						softpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/sftpanel/images/%s" % 'cardmini.png'))
				try:
					if 'softcam.' in line or 'cardserver.' in line:
						self.list.append((line, self.emuversion(line), softpng, typeemu))
				except:
					pass
		self.list.sort()
		self["menu"].setList(self.list)
		self.setTitle(_("Select SoftCam or CardServer: - %s") % config.plugins.sftpanel.activeemu.value)
		if self.indexpos is not None:
			self["menu"].setIndex(self.indexpos)
		self.name_in_memory()
	
	def emuversion(self, what):
		emuname = ' '
		nameemu = []
		if fileExists('/etc/init.d/%s' % what.split("\n")[0]):
			try:
				for line in open('/etc/init.d/%s' % what.split("\n")[0]):
					if 'echo' in line:
						nameemu.append(line)
				emuname =  '%s' % nameemu[1].split('"')[1]
			except:
				emuname = ' '
		return emuname
		
	def cut_name(self, what):
		count = 0
		what = what.replace('_', ' ').replace('-', ' ')
		count = len(what.split())
		if count <= 1:
			return what
		else:
			return what.split()[0]

	def name_in_memory(self):
		self.iConsole.ePopen("ps", self.stdout_find)

	def stdout_find(self, result, retval, extra_args):
		#if retval is 0:
		status = ''
		name_emu = self.cut_name(self.emuversion('softcam'))
		name_card = self.cut_name(self.emuversion('cardserver'))
		if name_card is not ' ':
			for line in result.splitlines(True):
				if name_card.split()[0].upper() in result.upper():
					status += '%s ' % name_card
					break
		if name_emu is not ' ':
			for line in result.splitlines(True):
				if name_emu.split()[0].upper() in result.upper():
					status += '%s' % name_emu
					break
		try:
			if status is not '':
				self["inmemory"].text = _('%s loaded in memory') % status
			else:
				self["inmemory"].text = _('not loaded modules')
		except Exception as e:
			now = time.localtime(time.time())
			logging('%02d:%02d:%d %02d:%02d:%02d - %s\r\n' % (now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec, str(e)))

	def listecm(self):
		self["text"].setText(ecm_view())
##################################################################################
	def ok(self):
		try:
			self.setTitle(_("Please wait"))
			self.emutype = self["menu"].getCurrent()[3]
			self.current_item = self["menu"].getCurrent()[0]
			if self["menu"].getCurrent()[1] != self.emuversion(self.emutype):
				self.indexpos = self["menu"].getIndex()
				self.session.openWithCallback(self.selemulist, start_cam, self.emutype, self.current_item)
		except Exception as e:
			now = time.localtime(time.time())
			logging('%02d:%02d:%d %02d:%02d:%02d - %s\r\n' % (now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec, str(e)))
##################################################################################
	def emuStopOperation(self):
		try:
			self.setTitle(_("Please wait"))
			self.emutype = self["menu"].getCurrent()[3]
			self.current_item = self["menu"].getCurrent()[0]
			if self.emuversion(self.emutype) != ' ':
				self.indexpos = self["menu"].getIndex()
				self.session.openWithCallback(self.selemulist, stop_cam, self.emutype)
		except Exception as e:
			now = time.localtime(time.time())
			logging('%02d:%02d:%d %02d:%02d:%02d - %s\r\n' % (now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec, str(e)))
##################################################################################
	def emuRestartOperation(self):
		try:
			self.setTitle(_("Please wait"))
			self.emutype = self["menu"].getCurrent()[3]
			if self.emuversion(self.emutype) is not ' ':
				self.indexpos = self["menu"].getIndex()
				self.session.openWithCallback(self.selemulist, restart_cam, self.emutype)
		except Exception as e:
			now = time.localtime(time.time())
			logging('%02d:%02d:%d %02d:%02d:%02d - %s\r\n' % (now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec, str(e)))

	def cancel(self):
		self.close()

	def switcher(self):
		status = True
		if fileExists('/etc/init.d/softcam'):
			for line in open('/etc/init.d/softcam'):
				if 'mgcamd' in line.lower():
					config.plugins.usw.activeconf.value = config.plugins.uswmgcamd.activeconf.value
					config.plugins.usw.configpath.value = config.plugins.uswmgcamd.configpath.value
					config.plugins.usw.emu.value = "Mgcamd"
					config.plugins.usw.configfile.value = config.plugins.uswmgcamd.configfile.value
					config.plugins.usw.configext.value = config.plugins.uswmgcamd.configext.value
				elif 'oscam' in line.lower():
					config.plugins.usw.activeconf.value = config.plugins.uswoscam.activeconf.value
					config.plugins.usw.configpath.value = config.plugins.uswoscam.configpath.value
					config.plugins.usw.emu.value = "Oscam"
					config.plugins.usw.configfile.value = config.plugins.uswoscam.configfile.value
					config.plugins.usw.configext.value = config.plugins.uswoscam.configext.value
				elif 'cccam' in line.lower():
					config.plugins.usw.activeconf.value = config.plugins.uswcccam.activeconf.value
					config.plugins.usw.configpath.value = config.plugins.uswcccam.configpath.value
					config.plugins.usw.emu.value = "CCcam"
					config.plugins.usw.configfile.value = config.plugins.uswcccam.configfile.value
					config.plugins.usw.configext.value = config.plugins.uswcccam.configext.value
				elif 'wicardd' in line.lower():
					config.plugins.usw.activeconf.value = config.plugins.uswwicardd.activeconf.value
					config.plugins.usw.configpath.value = config.plugins.uswwicardd.configpath.value
					config.plugins.usw.emu.value = "Wicardd"
					config.plugins.usw.configfile.value = config.plugins.uswwicardd.configfile.value
					config.plugins.usw.configext.value = config.plugins.uswwicardd.configext.value
				elif 'placeholder' in line.lower():
					status = False
			if status:
				self.session.open(uniswitcher)
			else:
				self.session.open(UniConfigScreen)
		else:
			self.session.open(UniConfigScreen)
#####################################################################################################
SKIN_DWN = """
<screen name="get_epg_data" position="center,140" size="625,35" title="Please wait">
  <widget source="status" render="Label" position="10,5" size="605,22" zPosition="2" font="Regular; 20" halign="center" transparent="2" />
</screen>"""
class start_cam(Screen):
	def __init__(self, session, emutype, current_item):
		Screen.__init__(self, session)
		self.session = session
		self.skin = SKIN_DWN
		self.emutype = emutype
		self.current_item = current_item
		self.setTitle(_("Please wait"))
		self["status"] = StaticText()
		self.iConsole = iConsole()
		self["status"].text = _("Stoping...")
		self.iConsole.ePopen("/etc/init.d/%s stop" % self.emutype, self.emuRemoveStartScript)

	def emuRemoveStartScript(self, result, retval, extra_args):
		self["status"].text = _("Removing startscript...")
		self.iConsole.ePopen("rm -f /etc/init.d/%s" % self.emutype, self.emuRemoveEcmInfo)

	def emuRemoveEcmInfo(self, result, retval, extra_args):
		self["status"].text = _("Removing ecm.info...")
		self.iConsole.ePopen("rm -f /tmp/ecm.info", self.emuAddStartScript)

	def emuAddStartScript(self, result, retval, extra_args):
		self["status"].text = _("Adding startscript...")
		self.iConsole.ePopen("ln -s /etc/init.d/%s /etc/init.d/%s" % (self.current_item, self.emutype),  self.emuChmodStartScript)

	def emuChmodStartScript(self, result, retval, extra_args):
		self.iConsole.ePopen("chmod 777 /etc/init.d/%s" %  self.emutype, self.emuScriptStart)

	def emuScriptStart(self, result, retval, extra_args):
		self["status"].text = _("Starting...")
		self.iConsole.ePopen("/etc/init.d/%s start" % self.emutype, self.sleep_time)
	
	def sleep_time(self, result, retval, extra_args):
		self.iConsole.ePopen("sleep 6", self.emuStartEndOperation)

	def emuStartEndOperation(self, result, retval, extra_args):
		config.plugins.sftpanel.activeemu.value = self.emuversion(self.emutype)
		config.plugins.sftpanel.activeemu.save()
		self["status"].setText(' ')
		self.close()

	def emuversion(self, what):
		emuname = ' '
		nameemu = []
		if fileExists('/etc/init.d/%s' % what.split("\n")[0]):
			try:
				for line in open('/etc/init.d/%s' % what.split("\n")[0]):
					if 'echo' in line:
						nameemu.append(line)
				emuname =  '%s' % nameemu[1].split('"')[1]
			except:
				emuname = ' '
		return emuname

class restart_cam(Screen):
	def __init__(self, session, emutype):
		Screen.__init__(self, session)
		self.session = session
		self.skin = SKIN_DWN
		self.emutype = emutype
		self.setTitle(_("Please wait"))
		self["status"] = StaticText()
		self.iConsole = iConsole()
		self["status"].text = _("Restarting...")
		self.iConsole.ePopen("/etc/init.d/%s restart" % self.emutype, self.sleep_time)
		
	def sleep_time(self, result, retval, extra_args):
		self.iConsole.ePopen("sleep 6", self.emuRestartOperationEnd)
		
	def emuRestartOperationEnd(self, result, retval, extra_args):
		self["status"].setText(' ')
		self.close()
####################################################################################################
class stop_cam(Screen):
	def __init__(self, session, emutype):
		Screen.__init__(self, session)
		self.session = session
		self.skin = SKIN_DWN
		self.emutype = emutype
		self.setTitle(_("Please wait"))
		self["status"] = StaticText()
		self.iConsole = iConsole()
		self["status"].text = _("Stoping...")
		self.iConsole.ePopen("/etc/init.d/%s stop" % self.emutype, self.emuRemoveScriptStop)
			
	def emuRemoveScriptStop(self, result, retval, extra_args):
		self["status"].text = _("Removing startscript...")
		self.iConsole.ePopen("rm -f /etc/init.d/%s" % self.emutype, self.emuRemoveEcmInfoStop)
			
	def emuRemoveEcmInfoStop(self, result, retval, extra_args):
		self["status"].text = _("Removing ecm.info...")
		self.iConsole.ePopen("rm -f /tmp/ecm.info", self.emuCreateNone)
			
	def emuCreateNone(self, result, retval, extra_args):
		self["status"].text = _("Creating None script...")
		if fileExists("/etc/init.d/%s.None" % self.emutype):
			self.iConsole.ePopen("ln -s /etc/init.d/%s.None /etc/init.d/%s" % (self.emutype, self.emutype),  self.emuChmodStopScript)
		elif fileExists("/etc/init.d/%s.none" % self.emutype):
			self.iConsole.ePopen("ln -s /etc/init.d/%s.none /etc/init.d/%s" % (self.emutype, self.emutype),  self.emuChmodStopScript)
		else:
			self.iConsole.ePopen("echo -e '# Placeholder for no cam' >> /etc/init.d/%s.None && ln -s /etc/init.d/%s.None /etc/init.d/%s" % \
				(self.emutype, self.emutype, self.emutype), self.emuChmodStopScript)
				
	def emuChmodStopScript(self, result, retval, extra_args):
		self.iConsole.ePopen("chmod 777 /etc/init.d/%s" %  self.emutype, self.sleep_time)
		
	def sleep_time(self, result, retval, extra_args):
		self.iConsole.ePopen("sleep 4", self.emuStopEndOperation)
		
	def emuStopEndOperation(self, result, retval, extra_args):
		self["status"].setText(' ')
		self.close()
####################################################################################################
class SoftcamPanel2(Screen):
	skin = """
<screen name="SoftcamPanel2" position="center,225" size="1300,720" title="SoftCam/CardServer Panel">
<ePixmap pixmap="MX_HQ7/menu/bb.png" position="18,638" size="1264,74" zPosition="-1" alphatest="on"/>
<ePixmap pixmap="MX_HQ7/menu/mainsoftcam.png" position="945,160" size="250,250" zPosition="-1" alphatest="on"/>
<ePixmap pixmap="MX_HQ7/menu/exitred.png" position="1212,650" size="48,48" alphatest="blend"/>
<ePixmap pixmap="MX_HQ7/buttons/green48x48.png" position="330,650" size="48,48" alphatest="blend"/>
<ePixmap pixmap="MX_HQ7/buttons/yellow48x48.png" position="630,650" size="48,48" alphatest="blend"/>
<ePixmap pixmap="MX_HQ7/buttons/blue48x48.png" position="930,650" size="48,48" alphatest="blend"/>
<ePixmap pixmap="MX_HQ7/menu/arrow1.png" position="40,650" size="48,48" alphatest="blend"/>
<ePixmap pixmap="MX_HQ7/menu/arrow_h.png" position="120,650" size="48,48" alphatest="blend"/>
<widget source="key_green" render="Label" position="390,640" size="250,70" zPosition="1" font="Regular;28" halign="left" valign="center" foregroundColor="button" backgroundColor="bgkey" transparent="1"/>
<widget source="menu" render="Listbox" enableWrapAround="1" position="20,20" size="820,605" zPosition="1" foregroundColor="button" backgroundColor="bgbutton" backgroundColorSelected="selbutton" backgroundPixmap="MX_HQ7/menu/bg820x55.png" selectionPixmap="MX_HQ7/menu/sel820x55.png" scrollbarMode="showNever" transparent="1">
<convert type="TemplatedMultiContent">
{"template": [ MultiContentEntryText(pos = (70, 9), size = (710, 35), flags = RT_HALIGN_LEFT, text =0),
MultiContentEntryPixmapAlphaTest(pos = (10, 7), size = (40, 40), png = 3), 
],
"fonts": [gFont("Regular",34)],
"itemHeight":55
}
</convert>
</widget>
<widget source="global.CurrentTime" render="Label" position="840,50" size="460,70" font="Regular;65" halign="center" foregroundColor="info" backgroundColor="bgmain" transparent="1">
<convert type="ClockToText">Default</convert>
</widget>
<widget source="session.CurrentService" render="Label" position="850,480" size="440,100" font="Regular;38" halign="center" foregroundColor="info" backgroundColor="bgmain" transparent="1">
<convert type="ServiceName">Name</convert>
</widget>
</screen>"""

	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self.indexpos = None
		self.setTitle(_("Service Cam"))
		#self["shortcuts"] = ActionMap(["ShortcutActions", "WizardActions"],
		self["shortcuts"] = NumberActionMap(["ShortcutActions", "WizardActions", "NumberActions"],
		{
			"ok": self.keyOK,
			"cancel": self.exit,
			"back": self.exit,
			"red": self.exit,
			"green": self.cccamupdate,
			"1": self.go,
			"2": self.go,
			"3": self.go,
		})
		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("update cfg"))
		self.list = []
		self["menu"] = List(self.list)
		self.mList()

	def cccamupdate(self):
		if fileExists('/media/usb/CCcam.cfg'):
			self.session.openWithCallback(self.inscccamcfg, MessageBox, _('Do you really want to install CCcam.cfg file from USB stick?'), MessageBox.TYPE_YESNO)
		else:
			self.mbox = self.session.open(MessageBox, _('CCcam.cfg file not found in /media/usb'), MessageBox.TYPE_ERROR, timeout=5)

	def inscccamcfg(self, answer):
		if answer is True:
			if fileExists('/media/usb/CCcam.cfg'):
				os.system('mv /etc/CCcam.cfg /etc/CCcam.cfg-saved')
				os.system('cp /media/usb/CCcam.cfg /etc/CCcam.cfg')
				self.info_message_cccamcfg()

	def info_message_cccamcfg(self):
		if fileExists('/etc/CCcam.cfg'):
			self.mbox = self.session.open(MessageBox, _('CCcam.cfg file successfully installed'), MessageBox.TYPE_INFO, timeout=5)
		else:
			self.mbox = self.session.open(MessageBox, _('CCcam.cfg file has not been installed'), MessageBox.TYPE_ERROR, timeout=5)

		
	def mList(self):
		self.list = []
		onepng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/sftpanel/images/softcam.png"))
		twopng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/sftpanel/images/unisw.png"))
		treepng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/sftpanel/images/panelcc.png"))
		cuatropng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/sftpanel/images/editorcc.png"))
		cincopng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/sftpanel/images/paneloscam.png"))
		self.list.append((_("Softcam/Cardserver"), 1, _("Start, Stop, Restart Sofcam/Cardserver"), onepng))
		self.list.append((_("Configuracion Cam"), 2, _("switch config files mgcamd, oscam, wicardd, cccam with remote conrol"), twopng))
		if Check_cccam():
			self.list.append((_("CCcam Panel"), 3, _("update Softcam.key from internet"), treepng))
			self.list.append((_("CCcam Editor"), 4, _("CCcam.cfg file easy editor"), cuatropng))
		if Check_oscam():
			self.list.append((_("oscam Panel"), 5, _("oscam manager"), cincopng))
           	if self.indexpos != None:
			self["menu"].setIndex(self.indexpos)
		self["menu"].setList(self.list)

	def exit(self):
		self.close()
		
	def go(self, num = None):
		if num is not None:
			num -= 1
			if not num < self["menu"].count():
				return
			self["menu"].setIndex(num)
		item = self["menu"].getCurrent()[1]
		self.select_item(item)

	def keyOK(self, item = None):
		if item == None:
			self.indexpos = self["menu"].getIndex()
			item = self["menu"].getCurrent()[1]
			self.select_item(item)

	def select_item(self, item):
		if item:
			if item is 1:
				self.session.open(emuSel5)
			elif item is 2:
				self.session.open(UniConfigScreen)
			elif item is 3:
				from Screens import CCcamInfo
            			self.session.open(CCcamInfo.CCcamInfoMain)
            		elif item is 4:
          	    		import ecccam
            			self.session.open(ecccam.ecccam_setup)
			elif item is 5:
          			sys.path.append('/usr/lib/enigma2/python/Plugins/SFteam/OscamInfo')
            			import oscaminfo
           			self.session.open(oscaminfo.OscamInfoMenu)
			else:
				self.close(None)

###############################################################################################

class uniswitcher(Screen):
	skin = """
<screen name="uniswitcher" position="center,225" size="1300,720" title="...">
   <ePixmap pixmap="MX_HQ7/menu/bb.png" position="18,638" size="1264,74" zPosition="-1" alphatest="on"/>
<ePixmap pixmap="MX_HQ7/menu/mainsoftcam.png" position="945,160" size="250,250" zPosition="-1" alphatest="on"/>
<ePixmap pixmap="MX_HQ7/menu/exit.png" position="1212,650" size="48,48" alphatest="blend"/>
<ePixmap pixmap="MX_HQ7/buttons/green48x48.png" position="330,650" size="48,48" alphatest="blend"/>
<ePixmap pixmap="MX_HQ7/buttons/yellow48x48.png" position="630,650" size="48,48" alphatest="blend"/>
<ePixmap pixmap="MX_HQ7/buttons/blue48x48.png" position="930,650" size="48,48" alphatest="blend"/>
<ePixmap pixmap="MX_HQ7/buttons/red48x48.png" position="30,650" size="48,48" alphatest="blend"/>
<widget source="key_red" render="Label" position="90,640" size="240,70" zPosition="1" font="Regular;32" halign="left" valign="center" foregroundColor="button" backgroundColor="bgkey" transparent="1"/>
<widget source="key_green" render="Label" position="390,640" size="250,70" zPosition="1" font="Regular;28" halign="left" valign="center" foregroundColor="button" backgroundColor="bgkey" transparent="1"/>
 <widget name="text" position="220,400" size="600,205" font="Regular;24" halign="center" noWrap="1" />
<widget source="menu" render="Listbox" enableWrapAround="1" position="20,20" size="820,605" zPosition="1" foregroundColor="button" backgroundColor="bgbutton" backgroundColorSelected="selbutton" backgroundPixmap="MX_HQ7/menu/bg820x55.png" selectionPixmap="MX_HQ7/menu/sel820x55.png" scrollbarMode="showNever" transparent="1">
<convert type="TemplatedMultiContent">
{"template": [ MultiContentEntryText(pos = (70, 9), size = (710, 35), flags = RT_HALIGN_LEFT, text =0),
MultiContentEntryPixmapAlphaTest(pos = (10, 7), size = (40, 40), png = 2), 
],
"fonts": [gFont("Regular",34)],
"itemHeight":55
}
</convert>
</widget>
<widget source="global.CurrentTime" render="Label" position="840,50" size="460,70" font="Regular;65" halign="center" foregroundColor="info" backgroundColor="bgmain" transparent="1">
<convert type="ClockToText">Default</convert>
</widget>
<widget source="session.CurrentService" render="Label" position="850,480" size="440,100" font="Regular;38" halign="center" foregroundColor="info" backgroundColor="bgmain" transparent="1">
<convert type="ServiceName">Name</convert>
</widget>
</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.iConsole = iConsole()
		self.skin = uniswitcher.skin
		self.setTitle(_("%s Switcher: - %s") % (config.plugins.usw.emu.value, config.plugins.usw.activeconf.value))
		self.session = session
		self.indexpos = None
		self.list = []
		self.servinactpng = LoadPixmap(path=resolveFilename(SCOPE_PLUGINS, "Extensions/sftpanel/images/serv.png"))
		self.servactpng = LoadPixmap(path=resolveFilename(SCOPE_PLUGINS, "Extensions/sftpanel/images/servact.png"))
		self["list"] = List(self.list)
		self["actions"] = ActionMap(["OkCancelActions", "ShortcutActions"],
		{	
			"ok": self.run,
			"red": self.close,
			"green": self.restartsoft,
			"cancel": self.close
		}, -1)
		self["readServ"] = StaticText()
		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Restart Softcam"))
		self["text"] = ScrollLabel("")
		self.listecm()
		self.Timer = eTimer()
		self.Timer.callback.append(self.listecm)
		self.Timer.start(1000*4, False)
		self.mList()
		
	def listecm(self):
		self["text"].setText(ecm_view())
		
	def mList(self):
		if config.plugins.usw.emu.value == "Mgcamd":
			config.plugins.usw.activeconf.value = config.plugins.uswmgcamd.activeconf.value
		elif config.plugins.usw.emu.value == "Wicardd":
			config.plugins.usw.activeconf.value = config.plugins.uswwicardd.activeconf.value
		elif config.plugins.usw.emu.value == "Oscam":
			config.plugins.usw.activeconf.value = config.plugins.uswoscam.activeconf.value
		elif config.plugins.usw.emu.value == "CCcam":
			config.plugins.usw.activeconf.value = config.plugins.uswcccam.activeconf.value
		self.list = []
		if os.path.exists(config.plugins.usw.configpath.value):
			list = os.listdir('%s' % config.plugins.usw.configpath.value)
			for line in list:
				if '.%s' % config.plugins.usw.configext.value in line:
					if line[:-3] == config.plugins.usw.activeconf.value:
						self.list.append((line[:-3],self.Adress(line), self.servactpng))
					else:
						self.list.append((line[:-3],self.Adress(line), self.servinactpng))
			self.list.sort()
			self["list"].setList(self.list)
			if self.indexpos != None:
				self["list"].setIndex(self.indexpos)
		
	def run(self):
		if self["list"].getCurrent() is not None:
			config.plugins.usw.activeconf.value = self["list"].getCurrent()[0]
			if config.plugins.usw.emu.value == "Mgcamd":
				config.plugins.uswmgcamd.activeconf.value = config.plugins.usw.activeconf.value
				config.plugins.uswmgcamd.activeconf.save()
			elif config.plugins.usw.emu.value == "Wicardd":
				config.plugins.uswwicardd.activeconf.value = config.plugins.usw.activeconf.value
				config.plugins.uswwicardd.activeconf.save()
			elif config.plugins.usw.emu.value == "Oscam":
				config.plugins.uswoscam.activeconf.value = config.plugins.usw.activeconf.value
				config.plugins.uswoscam.activeconf.save()
			elif config.plugins.usw.emu.value == "CCcam":
				config.plugins.uswcccam.activeconf.value = config.plugins.usw.activeconf.value
				config.plugins.uswcccam.activeconf.save()
			self.setTitle(_("%s Switcher: - %s") % (config.plugins.usw.emu.value, config.plugins.usw.activeconf.value))
			if  fileExists("%s/%s" % (config.plugins.usw.configpath.value, config.plugins.usw.configfile.value)):
				file_cfg = open('%s/%s' % (config.plugins.usw.configpath.value, config.plugins.usw.configfile.value), 'r').read()
				file_prv = open('%s/previous.%s' % (config.plugins.usw.configpath.value, config.plugins.usw.configext.value), 'w')
				file_prv.write(file_cfg)
				file_prv.close()
				os.chmod('%s/previous.%s' % (config.plugins.usw.configpath.value, config.plugins.usw.configext.value), 664)
			file_cfg = open('%s/%s.%s' % (config.plugins.usw.configpath.value, self["list"].getCurrent()[0], config.plugins.usw.configext.value), 'r').read()
			file_prv = open('%s/%s' % (config.plugins.usw.configpath.value, config.plugins.usw.configfile.value), 'w')
			file_prv.write(file_cfg)
			file_prv.close()
			os.chmod('%s/%s' % (config.plugins.usw.configpath.value, config.plugins.usw.configfile.value), 664)
			self.session.open(MessageBox, _("%s %s" % (self["list"].getCurrent()[0], config.plugins.usw.configfile.value)), type = MessageBox.TYPE_INFO, timeout = 6 )
			self.indexpos = self["list"].getIndex()
			self.mList()

	def restartsoft(self):
		clearlist = ""
		if fileExists("/etc/init.d/softcam"):
			self["text"].setText(clearlist)
			self.iConsole.ePopen("/etc/init.d/softcam restart")
		if fileExists("/etc/init.d/cardserver"):
			self["text"].setText(clearlist)
			self.iConsole.ePopen("/etc/init.d/cardserver restart")
		self.session.open(MessageBox, _("Softcam Restarted"), type = MessageBox.TYPE_INFO, timeout = 7 )

	def Adress (self, nameserv):
		cardline = ""
		iscard = 0
		if config.plugins.usw.emu.value == "Mgcamd":
			if fileExists("%s/%s" % (config.plugins.usw.configpath.value, nameserv)):
				for line in open("%s/%s" % (config.plugins.usw.configpath.value, nameserv)):
					if ("CWS =" in line or "CWS_MULTIPLE = " in line) and "CWS = 127.0.0.1" not in line:
						cardline = "serv: %s" % line.split()[2]
				return cardline 
		elif config.plugins.usw.emu.value == "Wicardd":
			if fileExists("%s/%s" % (config.plugins.usw.configpath.value, nameserv)):
				for line in open("%s/%s" % (config.plugins.usw.configpath.value, nameserv)):
					if "device" in line:
						cardline += "card: %s " % line.split()[-1]
					if "account" in line and not "[account]" in line and iscard < 1:
						cardline += "account: %s" % line.split()[-1].split("@")[-1].split(":")[0]
						iscard = iscard + 1
				return cardline
		elif config.plugins.usw.emu.value == "Oscam":
			if fileExists("%s/%s" % (config.plugins.usw.configpath.value, nameserv)):
				for line in open("%s/%s" % (config.plugins.usw.configpath.value, nameserv)):
					if "device" in line and "#" not in line:
						cardline += "card: %s " % line.split()[2]
					# card name change
					elif "internal" in line and "#" not in line:
						cardline += "card: %s " % line.split()[2].strip("]")
					if ("newcamd" in line and "[newcamd]" not in line) and iscard < 1 and "#" not in line:
						cardline += "serv: %s" % line.split()[2]
						iscard = iscard + 1
				return cardline
		elif config.plugins.usw.emu.value == "CCcam":
			if fileExists("%s/%s" % (config.plugins.usw.configpath.value, nameserv)):
				for line in open("%s/%s" % (config.plugins.usw.configpath.value, nameserv)):
					if "C:" in line and "#" not in line:
						cardline = line.split()[1]
				return cardline
		return ""

####################################################################################
class UniConfigScreen(ConfigListScreen, Screen):
	skin = """
<screen name="UniConfigScreen" position="center,225" size="1300,720" title="Configuracion Cam">
  <ePixmap pixmap="MX_HQ7/menu/bb.png" position="18,638" size="1264,74" zPosition="-1" alphatest="on"/>
<ePixmap pixmap="MX_HQ7/menu/menuconficam.png" position="945,160" size="250,250" zPosition="-1" alphatest="on"/>
<ePixmap pixmap="MX_HQ7/menu/exitred.png" position="1212,650" size="48,48" alphatest="blend"/>
<ePixmap pixmap="MX_HQ7/buttons/green48x48.png" position="330,650" size="48,48" alphatest="blend"/>
<ePixmap pixmap="MX_HQ7/buttons/yellow48x48.png" position="630,650" size="48,48" alphatest="blend"/>
<ePixmap pixmap="MX_HQ7/buttons/blue48x48.png" position="930,650" size="48,48" alphatest="blend"/>
<ePixmap pixmap="MX_HQ7/menu/arrow1.png" position="40,650" size="48,48" alphatest="blend"/>
<ePixmap pixmap="MX_HQ7/menu/arrow_h.png" position="120,650" size="48,48" alphatest="blend"/>
<widget source="key_green" render="Label" position="390,640" size="250,70" zPosition="1" font="Regular;28" halign="left" valign="center" foregroundColor="button" backgroundColor="bgkey" transparent="1"/>
<widget name="config" position="20,20" size="820,570" font="Regular;28" itemHeight="35" enableWrapAround="1" scrollbarMode="showOnDemand" foregroundColor="button" backgroundColor="bgbutton" backgroundColorSelected="selbutton" backgroundPixmap="MX_HQ7/menu/bg820x35.png" selectionPixmap="MX_HQ7/menu/button820x35.png" transparent="1"/>
<widget source="global.CurrentTime" render="Label" position="840,50" size="460,70" font="Regular;65" halign="center" foregroundColor="info" backgroundColor="bgmain" transparent="1">
<convert type="ClockToText">Default</convert>
</widget>
<widget source="session.CurrentService" render="Label" position="850,480" size="440,100" font="Regular;38" halign="center" foregroundColor="info" backgroundColor="bgmain" transparent="1">
<convert type="ServiceName">Name</convert>
</widget>
</screen>"""
	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self.setTitle(_("Configuracion Cam"))
		self.list = []
		self.list.append(getConfigListEntry(_("Mgcamd config switcher"), config.plugins.uswmgcamd.active))
		self.list.append(getConfigListEntry(_("Mgcamd configpath"), config.plugins.uswmgcamd.configpath))
		self.list.append(getConfigListEntry(_("Mgcamd config filename"), config.plugins.uswmgcamd.configfile))
		self.list.append(getConfigListEntry(_("Mgcamd configfile extention"), config.plugins.uswmgcamd.configext))
		self.list.append(getConfigListEntry(_("Wicardd config switcher"), config.plugins.uswwicardd.active))
		self.list.append(getConfigListEntry(_("Wicardd configpath"), config.plugins.uswwicardd.configpath))
		self.list.append(getConfigListEntry(_("Wicardd config filename"), config.plugins.uswwicardd.configfile))
		self.list.append(getConfigListEntry(_("Wicardd configfile extention"), config.plugins.uswwicardd.configext))
		self.list.append(getConfigListEntry(_("Oscam config switcher"), config.plugins.uswoscam.active))
		self.list.append(getConfigListEntry(_("Oscam configpath"), config.plugins.uswoscam.configpath))
		self.list.append(getConfigListEntry(_("Oscam config filename"), config.plugins.uswoscam.configfile))
		self.list.append(getConfigListEntry(_("Oscam configfile extention"), config.plugins.uswoscam.configext))
		self.list.append(getConfigListEntry(_("CCcam config switcher"), config.plugins.uswcccam.active))
		self.list.append(getConfigListEntry(_("CCcam configpath"), config.plugins.uswcccam.configpath))
		self.list.append(getConfigListEntry(_("CCcam config filename"), config.plugins.uswcccam.configfile))
		self.list.append(getConfigListEntry(_("CCcam configfile extention"), config.plugins.uswcccam.configext))
		ConfigListScreen.__init__(self, self.list)
		self["key_green"] = StaticText(_("Save"))
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
		{
			"red": self.cancel,
			"cancel": self.cancel,
			"green": self.save,
			"ok": self.save
		}, -2)

	def cancel(self):
		for i in self["config"].list:
			i[1].cancel()
		self.close(False)
		
	def save(self):
		for i in self["config"].list:
			i[1].save()
		configfile.save()
		from Components.PluginComponent import plugins
		plugins.reloadPlugins()
		self.mbox = self.session.open(MessageBox,(_("configuration is saved")), MessageBox.TYPE_INFO, timeout = 4 )
####################################################################################
