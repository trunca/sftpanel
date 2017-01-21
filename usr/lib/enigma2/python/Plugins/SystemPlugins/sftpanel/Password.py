from Components.ActionMap import ActionMap
from Components.config import config, ConfigText, ConfigSubsection, getConfigListEntry
from Components.ConfigList import ConfigListScreen
from Components.Language import language
from Components.ScrollLabel import ScrollLabel
from Components.Button import Button
from Components.Label import Label
from Components.Pixmap import Pixmap
from os import environ
from Plugins.Plugin import PluginDescriptor
from Screens.MessageBoxSF import MessageBoxSF
from Screens.Screen import Screen
from telnetlib import Telnet
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import gettext
from os import environ
config.plugins.PasswordChanger = ConfigSubsection()
config.plugins.PasswordChanger.old_password = ConfigText(default='', fixed_size=False)
config.plugins.PasswordChanger.new_password = ConfigText(default='', fixed_size=False)

class PasswordChanger(ConfigListScreen, Screen):
    skin = '\n\t\t<screen position="center,center" size="560,450" title="%s" >\n\t\t\t<widget name="config" position="center,center" size="540,70" scrollbarMode="showOnDemand" />\n\t\t\t<ePixmap name="red" position="85,410" zPosition="1" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />\n\t\t\t<ePixmap name="green" position="330,410" zPosition="1" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />\n\t\t\t<widget name="key_red" position="20,405" zPosition="2" size="270,50" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />\n\t\t\t<widget name="key_green" position="265,405" zPosition="2" size="270,50" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />\n\t\t</screen>' % _('Password Changer')

    def __init__(self, session, args = None):
        Screen.__init__(self, session)
        self.session = session
        ConfigListScreen.__init__(self, [getConfigListEntry(_('Old password:'), config.plugins.PasswordChanger.old_password), getConfigListEntry(_('New password:'), config.plugins.PasswordChanger.new_password)])
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'green': self.changePassword,
         'red': self.exit,
         'ok': self.changePassword,
         'cancel': self.exit}, -2)
        self['key_red'] = Label(_('Cancel'))
        self['key_green'] = Label(_('OK'))

    def changePassword(self):
        old_pass = config.plugins.PasswordChanger.old_password.value
        new_pass = config.plugins.PasswordChanger.new_password.value
        if len(new_pass) > 3 and len(new_pass) < 9:
            self.session.open(PasswordChangerConsole, old_pass, new_pass)
        else:
            self.session.open(MessageBoxSF, _('Incorrect new password!\nMinimum length: 4\nMaximum length: 8'), MessageBoxSF.TYPE_ERROR)

    def exit(self):
        for x in self['config'].list:
            x[1].cancel()

        self.close()


class PasswordChangerConsole(Screen):
    skin = '\n\t\t<screen position="center,center" size="560,450" title="%s" >\n\t\t\t<widget name="label" position="10,0" size="540,400" font="Regular;19" />\n\t\t\t<ePixmap name="green" position="215,410" zPosition="1" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />\n\t\t\t<widget name="key_green" position="150,405" zPosition="2" size="270,50" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />\n\t\t</screen>' % _('Password Changer')

    def __init__(self, session, old_pass, new_pass):
        Screen.__init__(self, session)
        self.working = True
        self.old_pass = old_pass
        self.new_pass = new_pass
        self.log = ''
        self.timeout = 2
        self['label'] = ScrollLabel('')
        self['key_green'] = Label(_('OK'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'green': self.exit,
         'ok': self.exit,
         'up': self['label'].pageUp,
         'down': self['label'].pageDown,
         'left': self['label'].pageUp,
         'right': self['label'].pageDown}, -1)
        self.onLayoutFinish.append(self.run)

    def exit(self):
        if not self.working:
            self.sendMessage('exit')
            self.close()

    def sendMessage(self, message):
        if self.t is not None:
            self.t.write(message + '\n')
            r = self.t.read_until('UNKNOWN', self.timeout)
            self.log += r
            return r
        else:
            return ''
            return

    def run(self):
        logged_in = False
        try:
            self.t = Telnet('localhost')
            self.log = self.t.read_until('login:', self.timeout)
            if self.log.__contains__('login:'):
                r = self.sendMessage('root')
                if r.__contains__('~#'):
                    logged_in = True
                elif r.__contains__('Password:'):
                    r = self.sendMessage(self.old_pass)
                    if r.__contains__('~#'):
                        logged_in = True
        except:
            self.t = None

        if logged_in:
            self.changePassword()
        else:
            self.log += _('Could not log in!')
            self['label'].setText(self.log)
            self.working = False
        return

    def changePassword(self):
        try:
            r = self.sendMessage('passwd')
            if r.__contains__('Enter new password:') or r.__contains__('New password:'):
                r = self.sendMessage(self.new_pass)
                if r.__contains__('Re-enter new password:') or r.__contains__('Retype password:'):
                    r = self.sendMessage(self.new_pass)
        except:
            self.log += _('Error while setting new password!')

        self['label'].setText(self.log)
        self.working = False