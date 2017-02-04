#by 2boom 4bob@ua.fm 2011-16
from Screens.Screen import Screen
from Screens.PluginBrowser import PluginBrowser
from Components.PluginComponent import plugins
from Screens.Standby import TryQuitMainloop
from Screens.MessageBox import MessageBox
from Components.Sources.StaticText import StaticText
from Components.Pixmap import Pixmap
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Sources.List import List
from Tools.LoadPixmap import LoadPixmap
from Components.Console import Console as iConsole
from Components.Label import Label
from Components.MenuList import MenuList
from Plugins.Plugin import PluginDescriptor
from Components.Language import language
from Tools.Directories import fileExists, pathExists, resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from Components.config import config, getConfigListEntry, ConfigText, ConfigPassword, ConfigClock, ConfigInteger, ConfigDateTime, ConfigSelection, ConfigSubsection, ConfigYesNo, configfile, NoSave
from Components.ConfigList import ConfigListScreen
from Components.Harddisk import harddiskmanager
from os import environ
import os
import gettext
import tools
from enigma import eEPGCache
from types import *
from enigma import *
import sys, traceback
import re
import time
import new
import _enigma
import enigma
import socket
import gzip
import urllib
import stat

global min, first_start
min = first_start = 0

lang = language.getLanguage()
environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("sftpanel", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "sftpanel/locale/"))

def _(txt):
	t = gettext.dgettext("sftpanel", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t
	
def mountp():
	pathmp = []
	if os.path.isfile('/proc/mounts'):
		for line in open('/proc/mounts'):
			if '/dev/sd' in line or '/dev/disk/by-uuid/' in line or '/dev/mmc' in line or '/dev/mtdblock' in line:
				pathmp.append(line.split()[1].replace('\\040', ' ') + '/')
	pathmp.append('/usr/share/enigma2/')
	pathmp.append('/tmp/')
	return pathmp
	
def logging(line):
	log_file = open('/tmp/sftpanel.log', 'a')
	log_file.write(line)
	log_file.close()

#now = time.localtime(time.time())
######################################################################################
config.plugins.sftpanel.filtername = ConfigYesNo(default = False)
config.plugins.sftpanel.currentclock = ConfigClock(default = 0)
config.plugins.sftpanel.multifilemode = ConfigSelection(default = "Multi", choices = [
		("Multi", _("Multi files")),
		("Single", _("Single file")),
])
config.plugins.sftpanel.userdir = ConfigText(default="/ipk/", visible_width = 70, fixed_size = False)
######################################################################################
class extrapanel(Screen):
	skin = """
<screen name="extrapanel" position="center,160" size="750,420" title="Extra Panel">
<ePixmap position="10,408" zPosition="1" size="165,2" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/sftpanel/images/red.png" alphatest="blend" />
<widget source="key_red" render="Label" position="10,378" zPosition="2" size="165,30" font="Regular;20" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="175,408" zPosition="1" size="165,2" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/sftpanel/images/green.png" alphatest="blend" />
<widget source="key_green" render="Label" position="175,378" zPosition="2" size="165,30" font="Regular;20" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="340,408" zPosition="1" size="165,2" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/sftpanel/images/yellow.png" alphatest="blend" />
<widget source="key_yellow" render="Label" position="340,378" zPosition="2" size="165,30" font="Regular;20" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="505,408" zPosition="1" size="165,2" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/sftpanel/images/blue.png" alphatest="blend" />
<widget source="key_blue" render="Label" position="505,378" zPosition="2" size="165,30" font="Regular;20" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<widget source="menu" render="Listbox" position="15,10" size="720,350" scrollbarMode="showOnDemand">
<convert type="TemplatedMultiContent">
	{"template": [
		MultiContentEntryText(pos = (50, 2), size = (600, 25), font=0, flags = RT_HALIGN_LEFT, text = 0), # index 2 is the Menu Titel
		MultiContentEntryText(pos = (60, 29), size = (600, 18), font=1, flags = RT_HALIGN_LEFT, text = 2), # index 3 is the Description
		MultiContentEntryPixmapAlphaTest(pos = (5, 5), size = (100, 40), png = 3), # index 4 is the pixmap
			],
	"fonts": [gFont("Regular", 23),gFont("Regular", 16)],
	"itemHeight": 50
	}
	</convert>
		</widget>
</screen>"""

	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self.setTitle(_("sft-panel"))
		self.iConsole = iConsole()
		self.indexpos = None
		self["shortcuts"] = NumberActionMap(["ShortcutActions", "WizardActions", "EPGSelectActions", "NumberActions"],
		{
			"ok": self.keyOK,
			"cancel": self.exit,
			"back": self.exit,
			"red": self.exit,
			"green": self.keyGreen,
			"yellow": self.keyYellow,
			"blue": self.keyBlue,
			"1": self.go,
			"2": self.go,
			"3": self.go,
			"4": self.go,
			"5": self.go,
			"6": self.go,
			"7": self.go,
		})
		self["key_green"] = StaticText(_("Informacion"))
		self["key_yellow"] = StaticText(_("Utilidades"))
		self["key_blue"] = StaticText(_("Instalar"))
		self["key_red"] = StaticText(_("Cerrar"))
		self.list = []
		self["menu"] = List(self.list)
		self.mList()

	def mList(self):
		self.list = []
		twopng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "SystemPlugins/sftpanel/images/tools.png"))
		treepng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "SystemPlugins/sftpanel/images/install.png"))
		fourpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "SystemPlugins/sftpanel/images/epp2.png"))
		sixpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "SystemPlugins/sftpanel/images/system.png"))
		sevenpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "SystemPlugins/sftpanel/images/addon.png"))
		eightpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "SystemPlugins/sftpanel/images/system2.png"))
		sietepng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "SystemPlugins/sftpanel/images/multimediapanel.png"))
		self.list.append((_("Utilidades de Servicio"), 2, _("Gestion EPG, NTP, ejecucion script...."), twopng ))
		self.list.append((_("Utilidades de Sistema"), 3, _("Gestion modulos Kernel, memoria swpa, Samba, utilidades usb"), sixpng ))
		self.list.append((_("Utilidades de Usuario"), 4, _("Liberador memoria, gestion cuenta Dns, utilidades password"), eightpng ))
		self.list.append((_("Instalar Paquetes"), 5, _("Gestion de instalacion de paquetes"), treepng))
		self.list.append((_("Acceso a Plugin"), 6, _("Gestion de plugins, instalacion y desistalacion"), sevenpng))
		self.list.append((_("Multimedia"), 7, _("Utilidades multimedia, streaming..."), sietepng))
		self.list.append((_("Panel Configuracion"), 8, _("Configuracion opciones Panel"), fourpng))
		if self.indexpos != None:
			self["menu"].setIndex(self.indexpos)
		self["menu"].setList(self.list)
		
	def go(self, num = None):
		if num is not None:
			num -= 1
			if not num < self["menu"].count():
				return
			self["menu"].setIndex(num)
		item = self["menu"].getCurrent()[1]
		self.select_item(item)
		
	def keyOK(self, item = None):
		self.indexpos = self["menu"].getIndex()
		if item == None:
			item = self["menu"].getCurrent()[1]
			self.select_item(item)

	def select_item(self, item):
		if item:
			if item is 2:				
				self.session.open(tools.ToolsScreen2)
			elif item is 3:
				self.session.open(tools.SystemScreen)
			elif item is 4:
				self.session.open(tools.System2Screen)
			elif item is 5:
				from Plugins.Extensions.MediaScanner.plugin import main
				main(self.session)
			elif item is 6:
				self.session.open(PluginBrowser)
			elif item is 7:
				self.session.open(tools.multimedia)
			elif item is 8:
				self.session.open(ConfigExtentions2)
			else:
				self.close(None)

	def exit(self):
		self.close()

	def keyBlue (self):
		from Plugins.Extensions.MediaScanner.plugin import main
		main(self.session)
				
	def keyYellow (self):
		self.session.open(tools.ToolsScreen2)
		
	def keyGreen (self):
		self.session.open(sftpanelinfo)
	
	
######################################################################################
class sftpanelinfo(Screen):
	skin = """
<screen name="sftpanelinfo" position="340,74" size="620,617" title="sft-panel">
	<ePixmap position="20,612" zPosition="1" size="180,2" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/sftpanel/images/red.png" alphatest="blend" />
	<widget source="CPULabel" render="Label" position="20,29" zPosition="2" size="180,22" font="Regular;20" halign="right" valign="center" backgroundColor="background" foregroundColor="#aaaaaa" transparent="1" />
	<widget source="CPU" render="Label" position="210,29" zPosition="2" size="390,22" font="Regular;20" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
	<widget source="key_red" render="Label" position="20,582" zPosition="2" size="180,30" font="Regular;20" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
	<widget source="MemoryLabel" render="Label" position="20,449" size="150,22" font="Regular; 20" halign="right" foregroundColor="#aaaaaa" />
	<widget source="SwapLabel" render="Label" position="20,473" size="150,22" font="Regular; 20" halign="right" foregroundColor="#aaaaaa" />
	<widget source="FlashLabel" render="Label" position="20,497" size="150,22" font="Regular; 20" halign="right" foregroundColor="#aaaaaa" />
	<widget source="memTotal" render="Label" position="180,449" zPosition="2" size="420,22" font="Regular;20" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
	<widget source="swapTotal" render="Label" position="180,473" zPosition="2" size="420,22" font="Regular;20" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
	<widget source="flashTotal" render="Label" position="180,497" zPosition="2" size="420,22" font="Regular;20" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
	<widget source="installedLabel" render="Label" position="20,125" zPosition="2" size="180,22" font="Regular;20" halign="right" valign="center" backgroundColor="background" foregroundColor="#aaaaaa" transparent="1" />
	<widget source="installed" render="Label" position="210,125" zPosition="2" size="390,22" font="Regular;20" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
	<widget source="device" render="Label" position="20,374" zPosition="2" size="580,66" font="Regular;20" halign="left" valign="top" backgroundColor="background" foregroundColor="foreground" transparent="1" />
	<widget source="Hardware" render="Label" position="210,5" zPosition="2" size="390,22" font="Regular;20" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
	<widget source="ipLabel" render="Label" position="20,53" zPosition="2" size="180,22" font="Regular;20" halign="right" valign="center" backgroundColor="background" foregroundColor="#aaaaaa" transparent="1" />
	<widget source="ipInfo" render="Label" position="210,53" zPosition="2" size="390,22" font="Regular;20" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
	<widget source="macLabel" render="Label" position="20,77" zPosition="2" size="180,22" font="Regular;20" halign="right" valign="center" backgroundColor="background" foregroundColor="#aaaaaa" transparent="1" />
	<widget source="macInfo" render="Label" position="210,77" zPosition="2" size="390,22" font="Regular;20" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
	<widget source="Image" render="Label" position="210,101" zPosition="2" size="390,22" font="Regular;20" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
	<widget source="Kernel" render="Label" position="210,149" zPosition="2" size="390,22" font="Regular;20" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
	<widget source="EnigmaVersion" render="Label" position="210,197" zPosition="2" size="390,22" font="Regular;20" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
	<widget source="HardwareLabel" render="Label" position="20,5" zPosition="2" size="180,22" font="Regular;20" halign="right" valign="center" backgroundColor="background" foregroundColor="#aaaaaa" transparent="1" />
	<widget source="ImageLabel" render="Label" position="20,101" zPosition="2" size="180,22" font="Regular;20" halign="right" valign="center" backgroundColor="background" foregroundColor="#aaaaaa" transparent="1" />
	<widget source="KernelLabel" render="Label" position="20,149" zPosition="2" size="180,22" font="Regular;20" halign="right" valign="center" backgroundColor="background" foregroundColor="#aaaaaa" transparent="1" />
	<widget source="EnigmaVersionLabel" render="Label" position="20,197" zPosition="2" size="180,22" font="Regular;20" halign="right" valign="center" backgroundColor="background" foregroundColor="#aaaaaa" transparent="1" />
	<widget source="gstreamerLabel" render="Label" position="20,221" zPosition="2" size="180,22" font="Regular;20" halign="right" valign="center" backgroundColor="background" foregroundColor="#aaaaaa" transparent="1" />
	<widget source="gstreamer" render="Label" position="210,221" zPosition="2" size="390,22" font="Regular;20" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
	<widget source="pythonLabel" render="Label" position="20,245" zPosition="2" size="180,22" font="Regular;20" halign="right" valign="center" backgroundColor="background" foregroundColor="#aaaaaa" transparent="1" />
	<widget source="python" render="Label" position="210,245" zPosition="2" size="390,22" font="Regular;20" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
	<widget source="nim" render="Label" position="20,277" zPosition="2" size="580,88" font="Regular;20" halign="left" valign="top" backgroundColor="background" foregroundColor="foreground" transparent="1" />
	<widget source="driver" render="Label" position="210,173" zPosition="2" size="390,22" font="Regular;20" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
	<widget source="driverLabel" render="Label" position="20,173" zPosition="2" size="180,22" font="Regular;20" halign="right" valign="center" backgroundColor="background" foregroundColor="#aaaaaa" transparent="1" />
	<eLabel position="30,271" size="560,2" backgroundColor="#aaaaaa" />
	<eLabel position="30,369" size="560,2" backgroundColor="#aaaaaa" />
	<eLabel position="30,443" size="560,2" backgroundColor="#aaaaaa" />
	<eLabel position="30,523" size="560,2" backgroundColor="#aaaaaa" />
	<eLabel position="230,558" size="320,2" backgroundColor="#aaaaaa" />
	<ePixmap position="20,531" size="180,47" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/sftpanel/images/sfpanelinfo.png" alphatest="blend" />
	<widget source="panelver" render="Label" position="490,531" zPosition="2" size="100,22" font="Regular;20" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
	<widget source="plipanel" render="Label" position="235,531" zPosition="2" size="250,22" font="Regular;20" halign="right" valign="center" backgroundColor="background" foregroundColor="#aaaaaa" transparent="1" />
	<widget source="cardserver" render="Label" position="370,590" zPosition="2" size="225,22" font="Regular;20" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
	<widget source="cardserverLabel" render="Label" position="235,590" zPosition="2" size="130,22" font="Regular;20" halign="right" valign="center" backgroundColor="background" foregroundColor="#aaaaaa" transparent="1" />
	<widget source="softcam" render="Label" position="370,566" zPosition="2" size="225,22" font="Regular;20" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
	<widget source="softcamLabel" render="Label" position="235,566" zPosition="2" size="130,22" font="Regular;20" halign="right" valign="center" backgroundColor="background" foregroundColor="#aaaaaa" transparent="1" />
</screen>"""

	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self.setTitle(_("sft-panel"))
		self.iConsole = iConsole()
		self["shortcuts"] = ActionMap(["ShortcutActions", "WizardActions"],
		{
			"cancel": self.cancel,
			"back": self.cancel,
			"red": self.cancel,
			"ok": self.cancel,
			})
		self["key_red"] = StaticText(_("Close"))
		self["MemoryLabel"] = StaticText(_("Memory:"))
		self["SwapLabel"] = StaticText(_("Swap:"))
		self["FlashLabel"] = StaticText(_("Flash:"))
		self["memTotal"] = StaticText()
		self["swapTotal"] = StaticText()
		self["flashTotal"] = StaticText()
		self["device"] = StaticText()
		self["installedLabel"] = StaticText(_("Installed Date:"))
		self["gstreamerLabel"] = StaticText(_("GStreamer:"))
		#self["livestreamerLabel"] = StaticText(_("Livestreamer:"))
		self["pythonLabel"] = StaticText(_("Python:"))
		self["installed"] = StaticText()
		self["gstreamer"] = StaticText()
		#self["livestreamer"] = StaticText()
		self["python"] = StaticText()
		self["Hardware"] = StaticText()
		self["Image"] = StaticText()
		self["CPULabel"] = StaticText(_("Processor:"))
		self["CPU"] = StaticText()
		self["Kernel"] = StaticText()
		self["nim"] = StaticText()
		self["ipLabel"] = StaticText(_("IP address:"))
		self["ipInfo"] = StaticText()
		self["macLabel"] = StaticText(_("MAC (lan/wlan):"))
		self["macInfo"] = StaticText()
		self["EnigmaVersion"] = StaticText()
		self["HardwareLabel"] = StaticText(_("Hardware:"))
		self["ImageLabel"] = StaticText(_("Image:"))
		self["KernelLabel"] = StaticText(_("Kernel Version:"))
		self["EnigmaVersionLabel"] = StaticText(_("Last Upgrade:"))
		self["driver"] = StaticText()
		self["driverLabel"] = StaticText(_("Driver Version:"))
		self["plipanel"] = StaticText(_("sft-panel Ver:"))
		self["panelver"] = StaticText()
		self["softcamLabel"] = StaticText(_("Softcam:"))
		self["softcam"] = StaticText()
		self["cardserverLabel"] = StaticText(_("Cardserver:"))
		self["cardserver"] = StaticText()
		self.memInfo()
		self.FlashMem()
		self.devices()
		self.mainInfo()
		self.verinfo()
		self.emuname()
		self.cpuinfo()
		self.getFlashDateString()
		self.getPythonVersionString()
		#self.getLivestreamerVersion()
		self.getGStreamerVersionString()
		self.network_info()
		
	def getLivestreamerVersion(self):
		if fileExists("/usr/lib/python2.7/site-packages/livestreamer/__init__.py"):
			for line in open("/usr/lib/python2.7/site-packages/livestreamer/__init__.py"):
				if '__version__' in line:
					self["livestreamer"].text = line.split('"')[1]
		else:
			self["livestreamer"].text = _("Not Installed")

	def network_info(self):
		self.iConsole.ePopen("ifconfig -a", self.network_result)
		
	def network_result(self, result, retval, extra_args):
		if retval is 0:
			ip = ''
			mac = []
			if len(result) > 0:
				for line in result.splitlines(True):
					if 'HWaddr' in line:
						mac.append('%s' % line.split()[-1].strip('\n'))
					elif 'inet addr:' in line and 'Bcast:' in line:
						ip = line.split()[1].split(':')[-1]
				self["macInfo"].text = '/'.join(mac)
			else:
				self["macInfo"].text =  _("unknown")
		else:
			self["macInfo"].text =  _("unknown")
		if ip is not '':
			self["ipInfo"].text = ip
		else:
			self["ipInfo"].text = _("unknown")

	def getGStreamerVersionString(self):
		import enigma
		try:
			self["gstreamer"].text =  enigma.getGStreamerVersionString().strip('GStreamer ')
		except:
			self["gstreamer"].text =  _("unknown")
		
	def getFlashDateString(self):
		try:
			self["installed"].text = time.strftime(_("%Y-%m-%d %H:%M"), time.localtime(os.stat("/boot").st_ctime))
		except:
			self["installed"].text =  _("unknown")
			
	def getPythonVersionString(self):
		try:
			import commands
			status, output = commands.getstatusoutput("python -V")
			self["python"].text =  output.split(' ')[1]
		except:
			self["python"].text =  _("unknown")
		
	def cpuinfo(self):
		if fileExists("/proc/cpuinfo"):
			cpu_count = 0
			processor = cpu_speed = cpu_family = cpu_variant = temp = ''
			core = _("core")
			cores = _("cores")
			for line in open('/proc/cpuinfo'):
				if "system type" in line:
					processor = line.split(':')[-1].split()[0].strip().strip('\n')
				elif "cpu MHz" in line:
					cpu_speed =  line.split(':')[-1].strip().strip('\n')
					#cpu_count += 1
				elif "cpu type" in line:
					processor = line.split(':')[-1].strip().strip('\n')
				elif "model name" in line:
					processor = line.split(':')[-1].strip().strip('\n').replace('Processor ', '')
				elif "cpu family" in line:
					cpu_family = line.split(':')[-1].strip().strip('\n')
				elif "cpu variant" in line:
					cpu_variant = line.split(':')[-1].strip().strip('\n')
				elif line.startswith('processor'):
					cpu_count += 1
			if not cpu_speed:
				try:
					cpu_speed = int(open("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq").read()) / 1000
				except:
					try:
						import binascii
						cpu_speed = int(int(binascii.hexlify(open('/sys/firmware/devicetree/base/cpus/cpu@0/clock-frequency', 'rb').read()), 16) / 100000000) * 100
					except:
						cpu_speed = '-'
			if fileExists("/proc/stb/sensors/temp0/value") and fileExists("/proc/stb/sensors/temp0/unit"):
				temp = "%s%s%s" % (open("/proc/stb/sensors/temp0/value").read().strip('\n'), unichr(176).encode("latin-1"), open("/proc/stb/sensors/temp0/unit").read().strip('\n'))
			elif fileExists("/proc/stb/fp/temp_sensor_avs"):
				temp = "%s%sC" % (open("/proc/stb/fp/temp_sensor_avs").read().strip('\n'), unichr(176).encode("latin-1"))
			if cpu_variant is '':
				self["CPU"].text = _("%s, %s Mhz (%d %s) %s") % (processor, cpu_speed, cpu_count, cpu_count > 1 and cores or core, temp)
			else:
				self["CPU"].text = "%s(%s), %s %s" % (processor, cpu_family, cpu_variant, temp)
		else:
			self["CPU"].text = _("undefined")

	def status(self):
		status = ''
		if fileExists("/usr/lib/opkg/status"):
			status = "/usr/lib/opkg/status"
		elif fileExists("/usr/lib/ipkg/status"):
			status = "/usr/lib/ipkg/status"
		elif fileExists("/var/lib/opkg/status"):
			status = "/var/lib/opkg/status"
		elif fileExists("/var/opkg/status"):
			status = "/var/opkg/status"
		return status
		
	def emuname(self):
		nameemu = []
		namecard = []
		if fileExists("/etc/init.d/softcam"):
			for line in open("/etc/init.d/softcam"):
				if "echo" in line:
					nameemu.append(line)
			try:
				self["softcam"].text =  "%s" % nameemu[1].split('"')[1]
			except:
				self["softcam"].text =  "Not Active"
		else:
			self["softcam"].text = _("Not Installed")
		if fileExists("/etc/init.d/cardserver"):
			for line in open("/etc/init.d/cardserver"):
				if "echo" in line:
					namecard.append(line)
			try:
				self["cardserver"].text = "%s" % namecard[1].split('"')[1]
			except:
				self["cardserver"].text =  "Not Active"
		else:
			self["cardserver"].text = _("Not Installed")
		
	def devices(self):
		list = ""
		hddlist = harddiskmanager.HDDList()
		hddinfo = ""
		if hddlist:
			for count in range(len(hddlist)):
				hdd = hddlist[count][1]
				if int(hdd.free()) > 1024:
					list += ((_("%s  %s  (%d.%03d GB free)\n") % (hdd.model(), hdd.capacity(), hdd.free()/1024 , hdd.free()%1024)))
				else:
					list += ((_("%s  %s  (%03d MB free)\n") % (hdd.model(), hdd.capacity(),hdd.free())))
		else:
			hddinfo = _("none")
		self["device"].text = list
		
	def HardWareType(self):
		if os.path.isfile("/proc/stb/info/boxtype"):
			return open("/proc/stb/info/boxtype").read().strip().upper()
		if os.path.isfile("/proc/stb/info/vumodel"):
			return "VU+" + open("/proc/stb/info/vumodel").read().strip().upper()
		if os.path.isfile("/proc/stb/info/model"):
			return open("/proc/stb/info/model").read().strip().upper()
		return _("unavailable")
		
	def getImageTypeString(self):
		try:
			if os.path.isfile("/etc/issue"):
				for line in open("/etc/issue"):
					if not line.startswith('Welcom') and '\l' in line:
						return line.capitalize().replace('\n', ' ').replace('\l', ' ').strip()
		except:
			pass
		return _("undefined")
		
	def getKernelVersionString(self):
		try:
			return open("/proc/version").read().split()[2]
		except:
			return _("unknown")
			
	def getImageVersionString(self):
		try:
			if os.path.isfile('/var/lib/opkg/status'):
				st = os.stat('/var/lib/opkg/status')
			elif os.path.isfile('/usr/lib/ipkg/status'):
				st = os.stat('/usr/lib/ipkg/status')
			elif os.path.isfile('/usr/lib/opkg/status'):
				st = os.stat('/usr/lib/opkg/status')
			elif os.path.isfile('/var/opkg/status'):
				st = os.stat('/var/opkg/status')
			tm = time.localtime(st.st_mtime)
			if tm.tm_year >= 2011:
				return time.strftime("%Y-%m-%d %H:%M:%S", tm)
		except:
			pass
		return _("unavailable")
		
	def listnims(self):
		tuner_name = {'0':'Tuner A:', '1':'Tuner B:', '2':'Tuner C:', '3':'Tuner D:', '4':'Tuner E:', '5':'Tuner F:', '6':'Tuner G:', '7':'Tuner H:', '8':'Tuner I:', '9':'Tuner J:'}
		nimlist = nims = ''
		allnims = []
		fbc_count = 0
		if fileExists("/proc/bus/nim_sockets"):
			for line in open("/proc/bus/nim_sockets"):
				if 'NIM Socket' in line:
					nimlist += tuner_name[line.split()[-1].replace(':', '')] + ' '
				elif 'Type:' in line:
					nimlist += '(%s)' % line.split()[-1].replace('\n', '').strip() + ' '
				elif 'Name:' in line:
					nimlist += '%s' % line.split(':')[1].replace('\n', '').strip() + '\n'					
			allnims = []
			fbc_count = nimlist.count('FBC')
			if fbc_count / 4 > 0:
				fbc = fbc_count / 4
				for line in nimlist.split('\n'):
					allnims.append(line)  
				for count in range(0, len(allnims)):
					if count < fbc:
						nims += allnims[count] + '\n'
					if count >= fbc * 4:
						nims += allnims[count] + '\n'
				return nims
			else:
				return nimlist
		else:
			return _("unavailable")
			
		nims = nimmanager.nimList(showFBCTuners=False)
		for count in range(len(nims)):
			if count < 4:
				self["Tuner" + str(count)] = StaticText(nims[count])
			else:
				self["Tuner" + str(count)] = StaticText("")
			AboutText += nims[count] + "\n"
			
	def mainInfo(self):
		package = 0
		self["Hardware"].text = self.HardWareType()
		self["Image"].text = self.getImageTypeString()
		self["Kernel"].text = self.getKernelVersionString()
		self["EnigmaVersion"].text = self.getImageVersionString()
		self["nim"].text = self.listnims()
		if fileExists(self.status()):
			for line in open(self.status()):
				if "-dvb-modules" in line and "Package:" in line:
					package = 1
				elif "kernel-module-player2" in line and "Package:" in line:
					package = 1
				elif "formuler-dvb-modules" in line and "Package:" in line:
					package = 1
				elif "vuplus-dvb-proxy-vusolo4k" in line and "Package:" in line:
					package = 1
				if "Version:" in line and package == 1:
					package = 0
					self["driver"].text = line.split()[-1]
					break

	def memInfo(self):
		for line in open("/proc/meminfo"):
			if "MemTotal:" in line:
				memtotal = line.split()[1]
			elif "MemFree:" in line:
				memfree = line.split()[1]
			elif "SwapTotal:" in line:
				swaptotal =  line.split()[1]
			elif "SwapFree:" in line:
				swapfree = line.split()[1]
		self["memTotal"].text = _("Total: %s Kb  Free: %s Kb") % (memtotal, memfree)
		self["swapTotal"].text = _("Total: %s Kb  Free: %s Kb") % (swaptotal, swapfree)
		
	def FlashMem(self):
		size = avail = 0
		st = os.statvfs("/")
		avail = st.f_bsize * st.f_bavail / 1024
		size = st.f_bsize * st.f_blocks / 1024
		self["flashTotal"].text = _("Total: %s Kb  Free: %s Kb") % (size , avail)
		
	def verinfo(self):
		package = 0
		self["panelver"].text = " "
		for line in open(self.status()):
			if "sftpanel" in line:
				package = 1
			if "Version:" in line and package is 1:
				package = 0
				self["panelver"].text = line.split()[1]
				break
		
	def cancel(self):
		self.close()
######################################################################################
class ConfigExtentions2(ConfigListScreen, Screen):
	skin = """
<screen name="ConfigExtentions2" position="center,160" size="750,370" title="sft-panel Menu/Extensionmenu config">
		<widget position="15,10" size="720,300" name="config" scrollbarMode="showOnDemand" />
		<ePixmap position="10,358" zPosition="1" size="165,2" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/sftpanel/images/red.png" alphatest="blend" />
		<widget source="key_red" render="Label" position="10,328" zPosition="2" size="165,30" font="Regular;20" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
		<ePixmap position="175,358" zPosition="1" size="165,2" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/sftpanel/images/green.png" alphatest="blend" />
		<widget source="key_green" render="Label" position="175,328" zPosition="2" size="165,30" font="Regular;20" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
</screen>"""

	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self.setTitle(_("sft-panel Menu/Extensionmenu config"))
		self.list = []
		self.list.append(getConfigListEntry(_("Directorio Montaje"), config.plugins.sftpanel.userdir))
		self.list.append(getConfigListEntry(_("Seccion modo instalacion paquete"), config.plugins.sftpanel.multifilemode))
		self.list.append(getConfigListEntry(_("Filtrar nombre en descarga"), config.plugins.sftpanel.filtername))
		self.list.append(getConfigListEntry(_("Directorio script"), config.plugins.sftpanel.scriptpath))
		ConfigListScreen.__init__(self, self.list)
		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Save"))
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions", "EPGSelectActions"],
		{
			"red": self.cancel,
			"cancel": self.cancel,
			"green": self.save,
			"ok": self.save
		}, -2)
		
	def cancel(self):
		self.close(False)

	
	def save(self):
		for i in self["config"].list:
			i[1].save()
		configfile.save()
		self.mbox = self.session.open(MessageBox,(_("configuration is saved")), MessageBox.TYPE_INFO, timeout = 4 )
######################################################################################
class loadEPG():
	def __init__(self):
		self.dialog = None

	def gotSession(self, session):
		self.session = session
		self.iConsole = iConsole()
		if config.plugins.sftpanel.epgupdate.value:
			self.timer = enigma.eTimer() 
			self.timermin = enigma.eTimer() 
			self.timermin.callback.append(self.check_change_min)
			self.timer.callback.append(self.check_change)
			self.timermin.startLongTimer(30)
			self.timer.startLongTimer(60)

	def check_change(self):
		self.timer.stop()
		now = time.localtime(time.time())
		try:
			lenght_epgfile = int(urllib.urlopen(config.plugins.sftpanel.url.value).info()['content-length'])
			logging('%02d:%02d:%d %02d:%02d:%02d - size epg.tar.gz: %d bytes\r\n' % (now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec, lenght_epgfile))
			if config.plugins.sftpanel.leghtfile.value != lenght_epgfile:
				self.loadepgdat()
		except Exception as e:
			logging('%02d:%02d:%d %02d:%02d:%02d - %s\r\n' % (now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec,  str(e)))
		self.timer.startLongTimer(int(config.plugins.sftpanel.checkp.value) * 60)

	def check_change_min(self):
		self.timermin.stop()
		if not config.plugins.sftpanel.epgupdate.value and config.plugins.sftpanel.first.value:
			self.timer.stop()
		now = time.localtime(time.time())
		if config.plugins.sftpanel.first.value and config.plugins.sftpanel.epgupdate.value:
			config.plugins.sftpanel.first.value = False
			if os.path.isfile('%s%s' % (config.plugins.sftpanel.direct.value, config.plugins.sftpanel.epgname.value)):
				epgcache = new.instancemethod(_enigma.eEPGCache_load,None,eEPGCache)
				epgcache = eEPGCache.getInstance().load()
				logging('%02d:%02d:%d %02d:%02d:%02d - reload epg.dat\r\n' % (now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec))
				
		if config.plugins.sftpanel.checkepgfile.value and config.plugins.sftpanel.nocheck.value:
			if not os.path.isfile('%s%s' % (config.plugins.sftpanel.direct.value, config.plugins.sftpanel.epgname.value)):
				logging('%02d:%02d:%d %02d:%02d:%02d - restore epg.dat\r\n' % (now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec))
				self.loadepgdat()
		if now.tm_hour in (0, 4, 8, 12, 16, 20) and now.tm_min == 1:
			self.iConsole.ePopen("opkg update")
		self.timermin.startLongTimer(60)

	def loadepgdat(self):
		config.plugins.sftpanel.nocheck.value = False
		now = time.localtime(time.time())
		if os.path.isfile('%s%s' % (config.plugins.sftpanel.direct.value, config.plugins.sftpanel.epgname.value)):
			os.chmod('%s%s' % (config.plugins.sftpanel.direct.value, config.plugins.sftpanel.epgname.value), stat.S_IWRITE)
		try:
			if self.isServerOnline():
				config.plugins.sftpanel.leghtfile.value = int(urllib.urlopen(config.plugins.sftpanel.url.value).info()['content-length'])
				config.plugins.sftpanel.leghtfile.save()
				configfile.save()
				urllib.urlretrieve (config.plugins.sftpanel.url.value, '/tmp/epg.dat.gz')
				if os.path.isfile('/tmp/epg.dat.gz'):
					inFile = gzip.GzipFile('/tmp/epg.dat.gz', 'rb')
					s = inFile.read()
					inFile.close()
					outFile = file('%s%s' % (config.plugins.sftpanel.direct.value, config.plugins.sftpanel.epgname.value), 'wb')
					outFile.write(s)
					outFile.close()
					if os.path.isfile('/tmp/epg.dat.gz'):
						os.remove('/tmp/epg.dat.gz')
					epgcache = eEPGCache.getInstance()
					epgcache.flushEPG()
					epgcache = new.instancemethod(_enigma.eEPGCache_load,None,eEPGCache)
					epgcache = eEPGCache.getInstance().load()
					logging('%02d:%02d:%d %02d:%02d:%02d - Auto Donwload & Unzip epg.dat.gz successful\r\n' % (now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec))
					config.plugins.sftpanel.lastupdate.value = _('last epg.dat updated - %02d:%02d:%d %02d:%02d:%02d' % (now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec))
					config.plugins.sftpanel.lastupdate.save()
					configfile.save()
			else:
				logging('%02d:%02d:%d %02d:%02d:%02d - %s not respond\r\n' % (now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec, config.plugins.sftpanel.url.value.split('/')[2]))
		except Exception as e:
			config.plugins.sftpanel.lastupdate.value = _('update error epg.dat - %02d:%02d:%d %02d:%02d:%02d' % (now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec))
			config.plugins.sftpanel.lastupdate.save()
			logging('%02d:%02d:%d %02d:%02d:%02d - %s\r\n' % (now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec, str(e)))
		config.plugins.sftpanel.nocheck.value = True

	def isServerOnline(self):
		now = time.localtime(time.time())
		try:
			socket.gethostbyaddr(config.plugins.sftpanel.url.value.split('/')[2])
		except Exception as e:
			logging('%02d:%02d:%d %02d:%02d:%02d - %s\r\n' % (now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec, str(e)))
			return False
		return True

pEmu = loadEPG()
######################################################################################
def sessionstart(reason,session=None, **kwargs):
	if reason == 0:
		pEmu.gotSession(session)
######################################################################################
def main(session, **kwargs):
	session.open(extrapanel)

def menu(menuid, **kwargs):
	if menuid == "mainmenu":
		return [(_("sft-panel"), main, _("sft-panel_"), 48)]
	return []

def Plugins(**kwargs):
	list = [PluginDescriptor(name=_("Panel SFTeam"), description=_("Utilidades imagen Sfteam"), where = [PluginDescriptor.WHERE_EXTENSIONSMENU], fnc=main)]
	return list


