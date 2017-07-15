import base64
import getpass
import imp
import inspect
import os
import sys
import time
from os.path import expanduser
from burp import IBurpExtender
from burp import IContextMenuFactory
from burp import IMessageEditorController
from burp import ITab
from java.awt.event import ActionListener
from java.awt.event import MouseAdapter
from java.lang import Boolean
from java.util import ArrayList
from javax.swing import BorderFactory
from javax.swing import JFileChooser
from javax.swing import JLabel
from javax.swing import JMenuItem
from javax.swing import JOptionPane
from javax.swing import JPanel
from javax.swing import JPopupMenu
from javax.swing import JScrollPane
from javax.swing import JSplitPane
from javax.swing import JTabbedPane
from javax.swing import JTextArea
from javax.swing.event import ListSelectionListener
from javax.swing.table import JTableHeader
sys.path.insert(
    1,
    os.path.join(
        os.path.dirname(
            os.path.abspath(
                inspect.getfile(
                    inspect.currentframe()))),
        'libs'))
reload(os)
os.environ['LC_ALL'] = 'en_US.UTF-8'
os.environ['LANG'] = 'en_US.UTF-8'

from threading import Thread
from libs.models import BurpDatabaseModels, CampaignTableModel, CampaignTable, LibraryTableModel, LibraryTable, SettingsTableModel, SettingsTable, MessageTableModel, MessageTable, SuccessBooleanRenderer
from lightbulb.api.api import LightBulb
from lightbulb.api.api_native import LightBulb as LightBulbNative
from libs.handlers import BurpBrowserHandler, BurpBrowserFilterHandler, BurpSQLHandler, BurpHTTPHandler, NativeHandler
import socket


def get_free_tcp_port(host):
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind((host, 0))
    tcp.listen(1)
    port = tcp.getsockname()[1]
    tcp.close()
    return port

class myRequestResponse:
    """This is a class for maintaining the implemented
    request and the received response, similar to the one
    that Burp Suite api provides. However, this is mutable
    in contrast with Burp's api.
    """
    def setRequest(self, request):
        """
        Stores a provided request payload
        Args:
            request (str): The request payload
        Returns:
            None
        """
        self.request = request

    def setResponse(self, response):
        """
        Stores a provided response payload
        Args:
            response (str): The response payload
        Returns:
            None
        """
        self.response = response

    def getRequest(self):
        """
        Retrieves a previously provided request payload
        Args:
            None
        Returns:
            str: The request payload
        """
        return self.request

    def getResponse(self):
        """
        Retrieves a previously provided response payload
        Args:
            None
        Returns:
            str: The response payload
        """
        return self.response


class Redrawer():

    def __init__(self, inputarray):
        self.inputarray = inputarray
        pass

    def redraw(self):
        for x in self.inputarray:
            if x is not None:
                x.redrawTable()


def die():
    exit()


class BurpExtender(
        IBurpExtender,
        ITab,
        IMessageEditorController,
        IContextMenuFactory):

    def findSetting(self, name, domain):
        # Check if Campaign already exits
        for i in self._db.getActiveSettingIndexes(domain):
            if self._db.arrayOfSettings[i]._name == name:
                return self._db.arrayOfSettings[i]._value

    def findSelectedSettings(self, domain):
        # Check if Campaign already exits
        total = []
        for i in self._db.getActiveSettingIndexes(domain):
            if getattr(self._db.arrayOfSettings[i], "_value"):
                total.append(self._db.arrayOfSettings[i]._name)
        return total

    def findSelectedSettingsCategorized(self, domain, category):
        # Check if Campaign already exits
        total = []
        for i in self._db.getActiveSettingIndexes(domain):
            if getattr(self._db.arrayOfSettings[i], "_val" + repr(category)):
                total.append(self._db.arrayOfSettings[i]._name)
        return total

    def set_input(self, name, configuration, learntype):
        total_Regex = []
        total_Grammar = []
        if learntype == 'GOFA' or 'TREEGEN':
            category = 1
        if learntype == 'SFADIFF':
            category = 5
        if name == "TESTS":
            if learntype == "TREEGEN":
                print 'Error, input filters selected in Tests tab cannot be used. Please remove them from selection'
                JOptionPane.showMessageDialog(
                    self._splitpane,
                    'Error, input filters selected in Tests tab cannot be used. Please remove them from selection',
                    "Error",
                    JOptionPane.INFORMATION_MESSAGE)
                return {}
            category = category + 2

        total_Regex = self.findSelectedSettingsCategorized("Regex", category)
        total_Grammar = self.findSelectedSettingsCategorized("Grammar", category + 1)

        if len(total_Regex) > 0 and len(total_Grammar) > 0:
            print 'Error, Regex and Grammars cannot be processed together. Please select one of these categories'
            JOptionPane.showMessageDialog(
                self._splitpane,
                'Error, Regex and Grammars cannot be processed together. Please select one of these categories',
                "Error",
                JOptionPane.INFORMATION_MESSAGE)
            return {}

        if len(total_Grammar) > 1:
            print 'Error, only one Grammar can be processed at a time'
            JOptionPane.showMessageDialog(
                self._splitpane,
                'Error, only one Grammar can be processed at a time',
                "Error",
                JOptionPane.INFORMATION_MESSAGE)
            return {}

        if name == "SEED" and len(total_Grammar) > 0:
            print 'Error, Grammars cannot be used for SEED'
            JOptionPane.showMessageDialog(
                self._splitpane,
                'Error, Grammars cannot be used for SEED',
                "Error",
                JOptionPane.INFORMATION_MESSAGE)
            return {}

        if len(total_Grammar) > 0:
            configuration[
                name + '_FILE'] = '{library}/grammars/' + total_Grammar[0] + '.y'
            configuration[name + '_FILE_TYPE'] = 'GRAMMAR'
        else:
            configuration[name + '_FILE'] = None
            configuration[name + '_FILE_TYPE'] = None

        if len(total_Regex) > 0:
            if len(total_Regex) == 1 and not learntype == "TREEGEN":
                configuration[
                    name + '_FILE'] = '{library}/regex/' + total_Regex[0] + '.y'
                configuration[name + '_FILE_TYPE'] = 'FLEX'
            else:
                if learntype == "TREEGEN":
                    configuration['SEED_FILES_LIST'] = []
                    for filterfile in total_Regex:
                        configuration['SEED_FILES_LIST'].append(
                            '{library}/regex/' + filterfile + '.y')
                        configuration[name + '_FILE_TYPE'] = 'FLEX'
                else:
                    print 'Error, only one Regex can be processed at a time'
                    JOptionPane.showMessageDialog(
                        self._splitpane,
                        'Error, only one Regex can be processed at a time',
                        "Error",
                        JOptionPane.INFORMATION_MESSAGE)
                    return {}
        else:
            if name + '_FILE' not in configuration:
                configuration[name + '_FILE'] = None
                configuration[name + '_FILE_TYPE'] = None

        return configuration

    def prepare_distinguish(self, configuration):
        settings = self.findSelectedSettings('Tree')
        if len(settings) == 0:
            print 'Error, no distinguish tree was selected'
            JOptionPane.showMessageDialog(
                self._splitpane,
                'Error, no distinguish tree was selected',
                "Error",
                JOptionPane.INFORMATION_MESSAGE)
            return {}
        if len(settings) > 1:
            print 'Error, only one distinguish tree can be processed at a time'
            JOptionPane.showMessageDialog(
                self._splitpane,
                'Error, only one distinguish tree can be processed at a time',
                "Error",
                JOptionPane.INFORMATION_MESSAGE)
            return {}

        configuration['FILE'] = '{library}/trees/' + \
            self.findSelectedSettings('Tree')[0] + '.json'
        return configuration

    def prepare_learn(self, configuration, learntype='GOFA'):

        configuration['ALPHABET'] = self.findSetting('ALPHABET', 'Learning')
        configuration['SAVE'] = self.findSetting('SAVE', 'Learning')
        configuration['HANDLER'] = None
        configuration = self.set_input("SEED", configuration, learntype)
        configuration = self.set_input("TESTS", configuration, learntype)
        return configuration

    def prepare_gen(self, configuration):
        configuration['FILE_IN'] = None
        configuration['ALPHABET'] = self.findSetting('ALPHABET', 'Learning')
        configuration['RANDOM'] = self.findSetting('RANDOMSEED', 'Learning')
        paramVal = JOptionPane.showInputDialog(
            self._splitpane,
            "Please choose the name of the output tree",
            "Learning Attributes",
            JOptionPane.QUESTION_MESSAGE)
        if not paramVal:
            JOptionPane.showMessageDialog(
                self._splitpane,
                'Error, please type the name of the output tree',
                "Error",
                JOptionPane.INFORMATION_MESSAGE)
            return {}
        configuration['FILE_OUT'] = paramVal
        configuration = self.set_input("SEED", configuration, "TREEGEN")
        configuration['HANDLER'] = BurpHTTPHandler
        return configuration

    def prepare_mysql(self, configuration):
        configuration['SQLPARSE'] = self.findSetting('SQLPARSE', 'MySQL')
        configuration['HOST'] = self.findSetting('HOST', 'MySQL')
        configuration['PORT'] = self.findSetting('PORT', 'MySQL')
        configuration['USERNAME'] = self.findSetting('USERNAME', 'MySQL')
        configuration['PASSWORD'] = self.findSetting('PASSWORD', 'MySQL')
        configuration['DATABASE'] = self.findSetting('DATABASE', 'MySQL')
        configuration['PREFIX_QUERY'] = self.findSetting(
            'PREFIX_QUERY', 'MySQL')
        return configuration

    def prepare_browser(self, configuration):
        configuration['WSPORT'] = self.findSetting('WSPORT', 'Browser')
        configuration['WBPORT'] = self.findSetting('WBPORT', 'Browser')
        configuration['BROWSERPARSE'] = self.findSetting(
            'BROWSERPARSE', 'Browser')
        configuration['DELAY'] = self.findSetting('DELAY', 'Browser')
        configuration['HOST'] = self.findSetting('HOST', 'Browser')
        if configuration['WSPORT'] == 'RANDOM':
            configuration['WSPORT'] = get_free_tcp_port(configuration['HOST'])
        if configuration['WBPORT'] == 'RANDOM':
            configuration['WBPORT'] = get_free_tcp_port(configuration['HOST'])
        JOptionPane.showMessageDialog(
            self._splitpane,
            'Please navigate with your browser at ' +
            configuration['HOST'] +
            ':' +
            repr(
                configuration['WBPORT']),
            "Error",
            JOptionPane.INFORMATION_MESSAGE)
        return configuration

    def createLibraryTabs(self):
        self._libraryTabs = JTabbedPane()
        self.LearningViewer = JTabbedPane()
        self.DifferentialViewer = JTabbedPane()
        self._libraryTabs.addTab("Learning", self.LearningViewer)
        self._libraryTabs.addTab(
            "Differential Learning",
            self.DifferentialViewer)
        TreesViewer = LibraryTable(
            self, model=LibraryTableModel(
                self._db, "Tree"))
        ScrollTreesViewer = JScrollPane(TreesViewer)
        TreesViewer.redrawTable()
        self._libraryTabs.addTab("Tree", ScrollTreesViewer)
        self._callbacks.customizeUiComponent(self._libraryTabs)
        return self.LearningViewer, self.DifferentialViewer, TreesViewer

    def createLibrarySubTabs(self, jtabbedpane, subcategory):
        SeedsViewer = JTabbedPane()
        TestsViewer = JTabbedPane()
        # if subcategory == 1:
        jtabbedpane.addTab("Seeds", SeedsViewer)
        # if subcategory == 2:
        jtabbedpane.addTab("Tests", TestsViewer)
        self._callbacks.customizeUiComponent(jtabbedpane)
        return SeedsViewer, TestsViewer

    def createLibrarySubSubTabs(self, jtabbedpane, subcategory):
        RegexesViewer = LibraryTable(
            self, model=LibraryTableModel(
                self._db, "Regex", subcategory))
        # RegexesViewer.setAutoCreateRowSorter()
        ScrollRegexesViewer = JScrollPane(RegexesViewer)
        RegexesViewer.redrawTable()
        GrammarsViewer = LibraryTable(
            self, model=LibraryTableModel(
                self._db, "Grammar", subcategory + 1))
        # GrammarsViewer.setAutoCreateRowSorter()
        ScrollGrammarsViewer = JScrollPane(GrammarsViewer)
        GrammarsViewer.redrawTable()
        jtabbedpane.addTab("Regex", ScrollRegexesViewer)
        jtabbedpane.addTab("Grammar", ScrollGrammarsViewer)
        self._callbacks.customizeUiComponent(jtabbedpane)
        return RegexesViewer, GrammarsViewer

    def createLibrarySubSubTabs2(self, jtabbedpane, subcategory):
        RegexesViewer = LibraryTable(
            self, model=LibraryTableModel(
                self._db, "Regex", subcategory))
        ScrollRegexesViewer = JScrollPane(RegexesViewer)
        RegexesViewer.redrawTable()
        jtabbedpane.addTab("Regex", ScrollRegexesViewer)
        self._callbacks.customizeUiComponent(jtabbedpane)
        return RegexesViewer, None

    def createSettingsTabs(self):
        settignsTabs = JTabbedPane()
        self.ServerViewer = SettingsTable(
            self, model=SettingsTableModel(
                self._db, "Browser"))
        ScrollServerViewer = JScrollPane(self.ServerViewer)
        self.ServerViewer.redrawTable()
        self.MysqlViewer = SettingsTable(
            self, model=SettingsTableModel(
                self._db, "MySQL"))
        ScrollMysqlViewer = JScrollPane(self.MysqlViewer)
        self.MysqlViewer.redrawTable()
        self.LearningViewer = SettingsTable(
            self, model=SettingsTableModel(
                self._db, "Learning"))
        ScrollLearningViewer = JScrollPane(self.LearningViewer)
        self.LearningViewer.redrawTable()
        settignsTabs.addTab("Web Browser", ScrollServerViewer)
        settignsTabs.addTab("MySQL Client", ScrollMysqlViewer)
        settignsTabs.addTab("Learning", ScrollLearningViewer)
        self._callbacks.customizeUiComponent(settignsTabs)
        # TODO: consider adding the results when clicking the tab (lazy
        # instantiation) since it can get slow

        return settignsTabs

    def addRegex(self, value, path):
        # print value
        name = path
        if path[0:7] == "/regex/":
            name = path[7:]
        self._db.addSetting(name, False, "Regex", value[1], path)

    def addGrammar(self, value, path):
        name = path
        if path[0:10] == "/grammars/":
            name = path[10:]
        self._db.addSetting(name, False, "Grammar", value[1], path)

    def addTree(self, value, path):
        name = path
        if path[0:7] == "/trees/":
            name = path[7:]
        self._db.addSetting(name, False, "Tree", value[1], path)

    def registerExtenderCallbacks(self, callbacks):

        # keep a reference to our Burp callbacks object
        self._callbacks = callbacks
        # obtain an Burp extension helpers object
        self._helpers = callbacks.getHelpers()
        # set our extension name
        callbacks.setExtensionName("LightBulb Framework")

        self._db = BurpDatabaseModels()
        self._db.selfExtender = self
        self._db.addSetting("WSPORT", "RANDOM", "Browser")
        self._db.addSetting("WBPORT", "RANDOM", "Browser")
        self._db.addSetting("HOST", "localhost", "Browser")
        self._db.addSetting("BROWSERPARSE", "True", "Browser")
        self._db.addSetting("DELAY", "50", "Browser")
        self._db.addSetting("SQLPARSE", "True", "MySQL")
        self._db.addSetting("HOST", "127.0.0.1", "MySQL")
        self._db.addSetting("PORT", "3306", "MySQL")
        self._db.addSetting("USERNAME", "root", "MySQL")
        self._db.addSetting("PASSWORD", "root", "MySQL")
        self._db.addSetting("DATABASE", "fuzzing", "MySQL")
        self._db.addSetting(
            "PREFIX_QUERY",
            "SELECT id FROM a WHERE a = **;",
            "MySQL")
        self._db.addSetting("ALPHABET", "32-127", "Learning")
        self._db.addSetting("SAVE", False, "Learning")
        self._db.addSetting("RANDOM", False, "Learning")
        self._db.addSetting("SHOW", "false", "Learning")
        self._db.addSetting("NATIVE", "false", "Learning")
        self._db.addSetting("NATIVE_PATH", "e.g., result of 'which lightbulb'", "Learning")
        self.lightbulbapp = LightBulb()
        self.lightbulbapp_native = LightBulbNative()
        self.lightbulbapp.readlibrary(
            "", self.addRegex, self.addGrammar, self.addTree)
        self.lightbulbapp.readlibrary(
            "my_saved_models",
            self.addRegex,
            self.addGrammar,
            self.addTree)
        self.lightbulbapp.readlibrary(
            "my_saved_regex",
            self.addRegex,
            self.addGrammar,
            self.addTree)
        self.lightbulbapp.readlibrary(
            "my_saved_trees",
            self.addRegex,
            self.addGrammar,
            self.addTree)
        self.lightbulbapp.readlibrary(
            "my_saved_grammars",
            self.addRegex,
            self.addGrammar,
            self.addTree)

        # For saving/loading config
        self._fc = JFileChooser()

        # Used by ActionListeners
        selfExtender = self
        self._selectedColumn = -1
        self._selectedRow = -1

        # Table of Request (AKA Message) entries
        self._messageTable = MessageTable(
            self, model=MessageTableModel(self._db))
        messageScrollPane = JScrollPane(self._messageTable)
        self._messageTable.redrawTable()

        # Table of Fuzz entries
        self._CampaignTable = CampaignTable(
            self, model=CampaignTableModel(self._db))
        fuzzingScrollPane = JScrollPane(self._CampaignTable)
        self._CampaignTable.redrawTable()

        selfExtender.selectedPath = None
        selfExtender.selectedName = None
        selfExtender.specialcat = None

        # Semi-Generic Popup stuff
        def addPopup(component, popup):
            class genericMouseListener(MouseAdapter):

                def mousePressed(self, e):
                    if e.isPopupTrigger():
                        self.showMenu(e)

                def mouseReleased(self, e):
                    if e.isPopupTrigger():
                        self.showMenu(e)

                def showMenu(self, e):
                    if isinstance(component, JTableHeader):
                        table = component.getTable()
                        column = component.columnAtPoint(e.getPoint())
                        if isinstance(
                                table,
                                MessageTable) and column >= selfExtender._db.STATIC_MESSAGE_TABLE_COLUMN_COUNT or isinstance(
                                table,
                                CampaignTable) and column >= selfExtender._db.STATIC_USER_TABLE_COLUMN_COUNT:
                            selfExtender._selectedColumn = column
                        else:
                            return
                    else:
                        selfExtender._selectedRow = component.rowAtPoint(
                            e.getPoint())
                    popup.show(e.getComponent(), e.getX(), e.getY())
            component.addMouseListener(genericMouseListener())

        def addPopupEditArea(component, popup):
            class genericMouseListener(MouseAdapter):

                def mousePressed(self, e):
                    if e.isPopupTrigger():
                        self.showMenu(e)

                def mouseReleased(self, e):
                    if e.isPopupTrigger():
                        self.showMenu(e)

                def showMenu(self, e):
                    popup.show(e.getComponent(), e.getX(), e.getY())
            component.addMouseListener(genericMouseListener())

        class actionRunMessage(ActionListener):

            def actionPerformed(self, e):
                if selfExtender._selectedRow >= 0:
                    if selfExtender._selectedRow not in selfExtender._messageTable.getSelectedRows():
                        indexes = [
                            selfExtender._db.getMessageByRow(
                                selfExtender._selectedRow)._index]
                    else:
                        indexes = [selfExtender._db.getMessageByRow(
                            rowNum)._index for rowNum in selfExtender._messageTable.getSelectedRows()]
                    t = Thread(
                        target=selfExtender.runMessagesThread,
                        args=[indexes])
                    t.start()
                    selfExtender._selectedColumn = -1
                    # Redrawing the table happens in colorcode within the
                    # thread

        class actionLearningMessage(ActionListener):

            def actionPerformed(self, e):
                if selfExtender._selectedRow >= 0:
                    if selfExtender._selectedRow not in selfExtender._messageTable.getSelectedRows():
                        indexes = [
                            selfExtender._db.getMessageByRow(
                                selfExtender._selectedRow)._index]
                    else:
                        indexes = [selfExtender._db.getMessageByRow(
                            rowNum)._index for rowNum in selfExtender._messageTable.getSelectedRows()]
                    t = Thread(
                        target=selfExtender.LearningMessagesThread,
                        args=[indexes])
                    t.start()
                    selfExtender._selectedColumn = -1

        class actionDiffLearningMessage(ActionListener):

            def actionPerformed(self, e):
                if selfExtender._selectedRow >= 0:
                    if selfExtender._selectedRow not in selfExtender._messageTable.getSelectedRows():
                        indexes = [
                            selfExtender._db.getMessageByRow(
                                selfExtender._selectedRow)._index]
                    else:
                        indexes = [selfExtender._db.getMessageByRow(
                            rowNum)._index for rowNum in selfExtender._messageTable.getSelectedRows()]
                    t = Thread(
                        target=selfExtender.DiffLearningMessagesThread, args=[
                            indexes, 'WAF'])
                    t.start()
                    selfExtender._selectedColumn = -1

        class actionDiffLearningMessageBrowser(ActionListener):

            def actionPerformed(self, e):
                if selfExtender._selectedRow >= 0:
                    if selfExtender._selectedRow not in selfExtender._messageTable.getSelectedRows():
                        indexes = [
                            selfExtender._db.getMessageByRow(
                                selfExtender._selectedRow)._index]
                    else:
                        indexes = [selfExtender._db.getMessageByRow(
                            rowNum)._index for rowNum in selfExtender._messageTable.getSelectedRows()]
                    t = Thread(
                        target=selfExtender.DiffLearningMessagesThread, args=[
                            indexes, 'Browser'])
                    t.start()
                    selfExtender._selectedColumn = -1

        class actionDiffLearningMessageBrowserBrowser(ActionListener):

            def actionPerformed(self, e):
                if selfExtender._selectedRow >= 0:
                    if selfExtender._selectedRow not in selfExtender._messageTable.getSelectedRows():
                        indexes = [
                            selfExtender._db.getMessageByRow(
                                selfExtender._selectedRow)._index]
                    else:
                        indexes = [selfExtender._db.getMessageByRow(
                            rowNum)._index for rowNum in selfExtender._messageTable.getSelectedRows()]
                    t = Thread(
                        target=selfExtender.DiffLearningMessagesThread, args=[
                            indexes, 'BrowserBrowser'])
                    t.start()
                    selfExtender._selectedColumn = -1

        class actionDiffLearningMessageBrowserFilter(ActionListener):

            def actionPerformed(self, e):
                if selfExtender._selectedRow >= 0:
                    if selfExtender._selectedRow not in selfExtender._messageTable.getSelectedRows():
                        indexes = [
                            selfExtender._db.getMessageByRow(
                                selfExtender._selectedRow)._index]
                    else:
                        indexes = [selfExtender._db.getMessageByRow(
                            rowNum)._index for rowNum in selfExtender._messageTable.getSelectedRows()]
                    t = Thread(
                        target=selfExtender.DiffLearningMessagesThread, args=[
                            indexes, 'BrowserFilter'])
                    t.start()
                    selfExtender._selectedColumn = -1

        class actionDiffLearningMessageMySQL(ActionListener):

            def actionPerformed(self, e):
                if selfExtender._selectedRow >= 0:
                    if selfExtender._selectedRow not in selfExtender._messageTable.getSelectedRows():
                        indexes = [
                            selfExtender._db.getMessageByRow(
                                selfExtender._selectedRow)._index]
                    else:
                        indexes = [selfExtender._db.getMessageByRow(
                            rowNum)._index for rowNum in selfExtender._messageTable.getSelectedRows()]
                    t = Thread(
                        target=selfExtender.DiffLearningMessagesThread, args=[
                            indexes, 'MySQL'])
                    t.start()
                    selfExtender._selectedColumn = -1

        class actionDistinguish(ActionListener):

            def actionPerformed(self, e):
                if selfExtender._selectedRow >= 0:
                    if selfExtender._selectedRow not in selfExtender._messageTable.getSelectedRows():
                        indexes = [
                            selfExtender._db.getMessageByRow(
                                selfExtender._selectedRow)._index]
                    else:
                        indexes = [selfExtender._db.getMessageByRow(
                            rowNum)._index for rowNum in selfExtender._messageTable.getSelectedRows()]
                    t = Thread(
                        target=selfExtender.DistinguishThread,
                        args=[indexes])
                    t.start()
                    selfExtender._selectedColumn = -1

        class actionTreeGen(ActionListener):

            def actionPerformed(self, e):
                if selfExtender._selectedRow >= 0:
                    if selfExtender._selectedRow not in selfExtender._messageTable.getSelectedRows():
                        indexes = [
                            selfExtender._db.getMessageByRow(
                                selfExtender._selectedRow)._index]
                    else:
                        indexes = [selfExtender._db.getMessageByRow(
                            rowNum)._index for rowNum in selfExtender._messageTable.getSelectedRows()]
                    t = Thread(
                        target=selfExtender.TreeGenThread,
                        args=[indexes])
                    t.start()
                    selfExtender._selectedColumn = -1

        class actionClear(ActionListener):

            def actionPerformed(self, e):
                selfExtender._db.arrayOfMessages = ArrayList()
                selfExtender._messageTable.redrawTable()

        class actionRemoveMessage(ActionListener):

            def actionPerformed(self, e):
                if selfExtender._selectedRow >= 0:
                    if selfExtender._selectedRow not in selfExtender._messageTable.getSelectedRows():
                        indexes = [
                            selfExtender._db.getMessageByRow(
                                selfExtender._selectedRow)._index]
                    else:
                        indexes = [selfExtender._db.getMessageByRow(
                            rowNum)._index for rowNum in selfExtender._messageTable.getSelectedRows()]
                    for i in indexes:
                        selfExtender._db.delete_message(i)
                    selfExtender._selectedColumn = -1
                    selfExtender._messageTable.redrawTable()

        class actionRemoveCampaign(ActionListener):

            def actionPerformed(self, e):
                if selfExtender._selectedRow >= 0:
                    if selfExtender._selectedRow not in selfExtender._CampaignTable.getSelectedRows():
                        indexes = [
                            selfExtender._db.getCampaignByRow(
                                selfExtender._selectedRow)._index]
                    else:
                        indexes = [selfExtender._db.getCampaignByRow(
                            rowNum)._index for rowNum in selfExtender._CampaignTable.getSelectedRows()]
                    for i in indexes:
                        selfExtender._db.delete_campaign(i)
                    selfExtender._selectedColumn = -1
                    selfExtender._CampaignTable.redrawTable()

        class actionShowCampaignStats(ActionListener):

            def actionPerformed(self, e):
                if selfExtender._selectedRow >= 0:
                    if selfExtender._selectedRow not in selfExtender._CampaignTable.getSelectedRows():
                        indexes = [
                            selfExtender._db.getCampaignByRow(
                                selfExtender._selectedRow)._index]
                    else:
                        indexes = [selfExtender._db.getCampaignByRow(
                            rowNum)._index for rowNum in selfExtender._CampaignTable.getSelectedRows()]
                    for i in indexes:
                        results = ""
                        for x in selfExtender._db.arrayOfCampaigns[i]._Stats:
                            if len(x) == 2:
                                results = results + \
                                    x[0] + ":" + repr(x[1]) + "\n"
                        paramVal = JOptionPane.showMessageDialog(
                            selfExtender._splitpane, results, "Statistics", JOptionPane.INFORMATION_MESSAGE)
                        #
                        break

        class actionEditAreaSave(ActionListener):

            def actionPerformed(self, e):
                if selfExtender.selectedPath is None or selfExtender.selectedName is None:
                    paramVal = JOptionPane.showMessageDialog(
                        selfExtender._splitpane,
                        "No file is selected",
                        "Error",
                        JOptionPane.INFORMATION_MESSAGE)
                    return
                print selfExtender.selectedName
                paramVal = JOptionPane.showConfirmDialog(
                    selfExtender._splitpane,
                    "Are you sure? The file will be overwritten.",
                    "Save File",
                    JOptionPane.YES_NO_OPTION)
                if paramVal == JOptionPane.NO_OPTION:
                    return
                data = selfExtender._editArea.getText()
                location = selfExtender.selectedPath
                if "my_saved_" in location:
                    location = expanduser(
                        "~") + "/.LightBulb/" + selfExtender.selectedCat + "/" + selfExtender.selectedPath.split('/')[-1]
                try:
                    with open(location, 'r+') as f:
                        f.seek(0)
                        f.write(data)
                        f.truncate()
                    paramVal = JOptionPane.showMessageDialog(
                        selfExtender._splitpane,
                        "File saved as " + location,
                        "Success",
                        JOptionPane.INFORMATION_MESSAGE)
                except:
                    paramVal = JOptionPane.showMessageDialog(
                        selfExtender._splitpane,
                        "File was not saved, Please check user permissions",
                        "Error",
                        JOptionPane.INFORMATION_MESSAGE)

        class actionEditAreaSaveAs(ActionListener):

            def actionPerformed(self, e):
                if selfExtender.selectedPath is None or selfExtender.selectedName is None:
                    paramVal = JOptionPane.showMessageDialog(
                        selfExtender._splitpane,
                        "No file is selected",
                        "Error",
                        JOptionPane.INFORMATION_MESSAGE)
                    return
                print selfExtender.selectedName
                name = JOptionPane.showInputDialog(
                    selfExtender._splitpane,
                    "Select new Filename",
                    "Save File As",
                    JOptionPane.QUESTION_MESSAGE)
                if not name or len(name) == 0:
                    JOptionPane.showMessageDialog(
                        selfExtender._splitpane,
                        'File was not saved, the name was empty',
                        "Error",
                        JOptionPane.INFORMATION_MESSAGE)
                    return
                data = selfExtender._editArea.getText()
                print data
                category = selfExtender.selectedCat
                extension = selfExtender.selectedExt
                categorytype = selfExtender.selectedCatType
                specialcat = selfExtender.specialcat

                home = expanduser("~")
                timestr = time.strftime("%Y%m%d-%H%M%S")
                if not os.path.exists(home + "/.LightBulb/"):
                    os.makedirs(home + "/.LightBulb/")
                if not os.path.exists(home + "/.LightBulb/" + category):
                    os.makedirs(home + "/.LightBulb/" + category)

                if os.path.exists(
                    home +
                    "/.LightBulb/" +
                    category +
                    "/" +
                    name +
                        ".py"):
                    JOptionPane.showMessageDialog(
                        selfExtender._splitpane,
                        'File already exists. Please choose a different name',
                        "Error",
                        JOptionPane.INFORMATION_MESSAGE)
                    return

                ruleset_file_meta = open(
                    home + "/.LightBulb/" + category + "/" + name + ".py", "w")
                ruleset_file_meta.write(
                    "META = {\n\
                            'author': '" + getpass.getuser() + "',\n\
                            'description': 'Saved model on " + timestr + "',\n\
                            'type':'" + categorytype + "',\n\
                            'comments': []\n\
                    }")
                ruleset_file_meta.close()
                print "Saved Model", home + "/.LightBulb/" + category + "/" + name + ".py"

                newpath = home + "/.LightBulb/" + category + "/" + name + extension
                try:
                    ruleset_file = open(
                        home +
                        "/.LightBulb/" +
                        category +
                        "/" +
                        name +
                        extension,
                        "w")
                    ruleset_file.write(data)
                    ruleset_file.close()
                    paramVal = JOptionPane.showMessageDialog(
                        selfExtender._splitpane,
                        "File saved as " +
                        newpath +
                        " and added to your library.",
                        "Success",
                        JOptionPane.INFORMATION_MESSAGE)
                except:
                    print sys.exc_info()
                    paramVal = JOptionPane.showMessageDialog(
                        selfExtender._splitpane,
                        "File was not saved, Please check user permissions",
                        "Error",
                        JOptionPane.INFORMATION_MESSAGE)
                print specialcat + "/" + name, False, categorytype, 'Saved model on ' + timestr, specialcat + "/" + name
                selfExtender._db.addSetting(
                    specialcat + "/" + name,
                    False,
                    categorytype,
                    'Saved model on ' + timestr,
                    specialcat + "/" + name)
                selfExtender.libraryredraw.redraw()

        class actionEditAreaShowPath(ActionListener):

            def actionPerformed(self, e):
                if selfExtender.selectedPath is None or selfExtender.selectedName is None:
                    paramVal = JOptionPane.showMessageDialog(
                        selfExtender._splitpane,
                        "No file is selected",
                        "Error",
                        JOptionPane.INFORMATION_MESSAGE)
                    return
                location = selfExtender.selectedPath
                if "my_saved_" in location:
                    print location
                    location = expanduser(
                        "~") + "/.LightBulb/" + selfExtender.selectedCat + "/" + selfExtender.selectedPath.split('/')[-1]
                    print location
                paramVal = JOptionPane.showMessageDialog(
                    selfExtender._splitpane,
                    location,
                    "Location in Filesystem:",
                    JOptionPane.INFORMATION_MESSAGE)

        # Message Table popups
        messagePopup = JPopupMenu()
        addPopup(self._messageTable, messagePopup)
        messageRun = JMenuItem("Test Request(s)")
        messageRun.addActionListener(actionRunMessage())
        messagePopup.add(messageRun)
        messageRemove = JMenuItem("Remove Request(s)")
        messageRemove.addActionListener(actionRemoveMessage())
        messagePopup.add(messageRemove)
        messageLearning = JMenuItem("Start Filter Learning")
        messageLearning.addActionListener(actionLearningMessage())
        messagePopup.add(messageLearning)
        messageDiffLearning = JMenuItem(
            "Start Filters(s) Differential Learning (Select (2) Requests)")
        messageDiffLearning.addActionListener(actionDiffLearningMessage())
        messagePopup.add(messageDiffLearning)
        messageDiffLearningMySQL = JMenuItem(
            "Start Filter Differential Learning with MySQL")
        messageDiffLearningMySQL.addActionListener(
            actionDiffLearningMessageMySQL())
        messagePopup.add(messageDiffLearningMySQL)
        messageDiffLearningBrowser = JMenuItem(
            "Start Filter Differential Learning with Browser")
        messageDiffLearningBrowser.addActionListener(
            actionDiffLearningMessageBrowser())
        messagePopup.add(messageDiffLearningBrowser)
        messageDiffLearningBrowserFilter = JMenuItem(
            "Start Filter Differential Learning with Browser Filter")
        messageDiffLearningBrowserFilter.addActionListener(
            actionDiffLearningMessageBrowserFilter())
        messagePopup.add(messageDiffLearningBrowserFilter)
        messageDistinguish = JMenuItem("Start Filters(s) WAF Distinguish")
        messageDistinguish.addActionListener(actionDistinguish())
        messagePopup.add(messageDistinguish)
        messageDistinguishTree = JMenuItem(
            "Start Filters(s) Distinguish Tree Generation")
        messageDistinguishTree.addActionListener(actionTreeGen())
        messagePopup.add(messageDistinguishTree)
        messageBrowserDiffLearning = JMenuItem(
            "Start Browsers Differential Learning")
        messageBrowserDiffLearning.addActionListener(actionDiffLearningMessageBrowserBrowser())
        messagePopup.add(messageBrowserDiffLearning)
        messageDistinguishTree = JMenuItem("Clear all requests")
        messageDistinguishTree.addActionListener(actionClear())
        messagePopup.add(messageDistinguishTree)

        # Campaign Table popup
        campaignPopup = JPopupMenu()
        addPopup(self._CampaignTable, campaignPopup)
        campaignRemove = JMenuItem("Terminate and Remove Campaign(s)")
        campaignRemove.addActionListener(actionRemoveCampaign())
        campaignPopup.add(campaignRemove)

        campaignStats = JMenuItem("Check Stats/Result")
        campaignStats.addActionListener(actionShowCampaignStats())
        campaignPopup.add(campaignStats)

        ##########
        #
        # TEXTAREA
        #
        ##########
        self._editArea = JTextArea(10, 50)
        self._editArea.setLineWrap(True)
        self._editArea.setEditable(True)
        self._editArea.border = BorderFactory.createEmptyBorder(2, 2, 2, 2)

        editAreaPopup = JPopupMenu()
        addPopupEditArea(self._editArea, editAreaPopup)
        editAreaSave = JMenuItem("Save File")
        editAreaSave.addActionListener(actionEditAreaSave())
        editAreaPopup.add(editAreaSave)
        editAreaSaveAs = JMenuItem("Save File As")
        editAreaSaveAs.addActionListener(actionEditAreaSaveAs())
        editAreaPopup.add(editAreaSaveAs)
        editAreaShowPath = JMenuItem("Show Location")
        editAreaShowPath.addActionListener(actionEditAreaShowPath())
        editAreaPopup.add(editAreaShowPath)

        scrollingText = JScrollPane(self._editArea)

        ##########
        #
        # select row listener
        #
        ##########
        class selectListener(ListSelectionListener):

            def __init__(self, parent, editarea, app):
                self.parent = parent
                self.editarea = editarea
                self.lightbulbapp = app

            def valueChanged(self, e):
                status = e.valueIsAdjusting
                if not status:
                    wrapper = e.source.getMaxSelectionIndex()
                    if wrapper < 0:
                        return
                    print self.parent.model._db.getSettingByRow(wrapper, self.parent.model._domain)._name
                    #reader = FileReader(self.parent.model._db.getSettingByRow(wrapper,self.parent.model._domain)._name)

                    self.editarea.replaceRange(
                        None, 0, len(self.editarea.getText()))
                    print self.parent.model._db.getSettingByRow(wrapper, self.parent.model._domain)._path[1:]
                    data = self.lightbulbapp.readlibraryfile(
                        self.parent.model._db.getSettingByRow(
                            wrapper, self.parent.model._domain)._path)
                    print data[1][0][1]

                    extension = ""
                    if self.parent.model._domain == "Regex":
                        extension = ".y"
                        selfExtender.selectedCat = "regex"
                        selfExtender.specialcat = "my_saved_regex"
                    if self.parent.model._domain == "Grammar":
                        extension = ".y"
                        selfExtender.selectedCat = "grammars"
                        selfExtender.specialcat = "my_saved_grammars"
                    if self.parent.model._domain == "Tree":
                        extension = ".json"
                        selfExtender.selectedCat = "trees"
                        selfExtender.specialcat = "my_saved_trees"

                    selfExtender.selectedPath = imp.find_module('lightbulb')[
                        1] + '/data/' + self.parent.model._db.getSettingByRow(wrapper, self.parent.model._domain)._path + extension
                    selfExtender.selectedName = self.parent.model._db.getSettingByRow(
                        wrapper, self.parent.model._domain)._name
                    selfExtender.selectedExt = extension
                    selfExtender.selectedCatType = self.parent.model._domain

                    self.editarea.append(data[1][0][1])
        ##########
        #
        # LIBRARY
        #
        ##########
        self.LearningViewer, self.DifferentialViewer, self.trees = self.createLibraryTabs()
        self.LearningViewerSeedsViewer, self.LearningViewerTestsViewer = self.createLibrarySubTabs(
            self.LearningViewer, 1)
        self.DifferentialViewerSeedsViewer, self.DifferentialViewerTestsViewer = self.createLibrarySubTabs(
            self.DifferentialViewer, 2)

        self.LearningViewerTestsViewerRegexesViewer, self.LearningViewerTestsViewerGrammarsViewer = self.createLibrarySubSubTabs(
            self.LearningViewerTestsViewer, 3)
        self.LearningViewerSeedsViewerRegexesViewer, self.LearningViewerSeedsViewerGrammarsViewer = self.createLibrarySubSubTabs2(
            self.LearningViewerSeedsViewer, 1)
        self.DifferentialViewerTestsViewerRegexesViewer, self.DifferentialViewerTestsViewerGrammarsViewer = self.createLibrarySubSubTabs(
            self.DifferentialViewerTestsViewer, 7)
        self.DifferentialViewerSeedsViewerRegexesViewer, self.DifferentialViewerSeedsViewerGrammarsViewer = self.createLibrarySubSubTabs2(
            self.DifferentialViewerSeedsViewer, 5)

        self.LearningViewerSeedsViewerRegexesViewer.getSelectionModel().addListSelectionListener(
            selectListener(self.LearningViewerSeedsViewerRegexesViewer, self._editArea, self.lightbulbapp))
        #self.LearningViewerSeedsViewerGrammarsViewer.getSelectionModel().addListSelectionListener(selectListener(self.LearningViewerSeedsViewerGrammarsViewer, self._editArea, self.lightbulbapp));
        self.LearningViewerTestsViewerRegexesViewer.getSelectionModel().addListSelectionListener(
            selectListener(self.LearningViewerTestsViewerRegexesViewer, self._editArea, self.lightbulbapp))
        self.LearningViewerTestsViewerGrammarsViewer.getSelectionModel().addListSelectionListener(
            selectListener(self.LearningViewerTestsViewerGrammarsViewer, self._editArea, self.lightbulbapp))

        self.DifferentialViewerSeedsViewerRegexesViewer.getSelectionModel().addListSelectionListener(
            selectListener(self.DifferentialViewerSeedsViewerRegexesViewer, self._editArea, self.lightbulbapp))
        #self.DifferentialViewerSeedsViewerGrammarsViewer.getSelectionModel().addListSelectionListener(selectListener(self.DifferentialViewerSeedsViewerGrammarsViewer, self._editArea, self.lightbulbapp));
        self.DifferentialViewerTestsViewerRegexesViewer.getSelectionModel().addListSelectionListener(
            selectListener(self.DifferentialViewerTestsViewerRegexesViewer, self._editArea, self.lightbulbapp))
        self.DifferentialViewerTestsViewerGrammarsViewer.getSelectionModel().addListSelectionListener(
            selectListener(self.DifferentialViewerTestsViewerGrammarsViewer, self._editArea, self.lightbulbapp))

        self.trees.getSelectionModel().addListSelectionListener(
            selectListener(self.trees, self._editArea, self.lightbulbapp))

        selfExtender.libraryredraw = Redrawer([
            self.LearningViewerTestsViewerRegexesViewer,
            self.LearningViewerTestsViewerGrammarsViewer,
            self.LearningViewerSeedsViewerRegexesViewer,
            self.LearningViewerSeedsViewerGrammarsViewer,
            self.DifferentialViewerTestsViewerRegexesViewer,
            self.DifferentialViewerTestsViewerGrammarsViewer,
            self.DifferentialViewerSeedsViewerRegexesViewer,
            self.DifferentialViewerSeedsViewerGrammarsViewer,
            self.trees])
        ##########
        #
        # SETTINGS
        #
        ##########
        self.settings = self.createSettingsTabs()
        self._libraryTabs.addTab("Settings", self.settings)

        self.about = JPanel()
        content = JLabel('')
        content.setText('<html><body><center><h3>LightBulb Framework</h3></center><table><tr><td style="width: 80px;max-width:80px;overflow:hidden;"><img src="https://lightbulb-framework.github.io/assets/images/logo5notitle-th.png" width=\'65\'  height=\'95\'/></td><td><p>- George Argyros (argyros.george@gmail.com)</p><p>- Ioannis Stais (ioannis.stais@gmail.com)</p><br><p>A joint work with:</p><p>- Suman Jana</p><p>- Angelos D. Keromytis</p><p>- Aggelos Kiayias</p><p>Learn More: https://lightbulb-framework.github.io</p></td></tr></table></body></html>')
        self.about.add(content)
        self._libraryTabs.addTab("About", JScrollPane(self.about))

        count = self._libraryTabs.getTabCount()
        self._libraryTabs.setSelectedIndex(count - 1)

        topPanePart = JSplitPane(
            JSplitPane.HORIZONTAL_SPLIT,
            self._libraryTabs,
            scrollingText)
        topPanePart.setDividerLocation(800)

        # Top pane
        middlePanePart = JSplitPane(
            JSplitPane.HORIZONTAL_SPLIT,
            messageScrollPane,
            fuzzingScrollPane)
        middlePanePart.setDividerLocation(800)

        topPane = JSplitPane(
            JSplitPane.VERTICAL_SPLIT,
            topPanePart,
            middlePanePart)
        topPane.setDividerLocation(200)

        # request tabs added to this tab on click in message table
        self._tabs = JTabbedPane()

        # bottomPane = JSplitPane(JSplitPane.VERTICAL_SPLIT, self._tabs, buttons)
        # bottomPane.setDividerLocation(200)
        # Main Pane
        self._splitpane = JSplitPane(
            JSplitPane.VERTICAL_SPLIT, topPane, self._tabs)
        self._splitpane.setDividerLocation(500)

        # customize our UI components
        callbacks.customizeUiComponent(self._splitpane)
        callbacks.customizeUiComponent(topPane)
        # callbacks.customizeUiComponent(bottomPane)
        callbacks.customizeUiComponent(messageScrollPane)
        callbacks.customizeUiComponent(fuzzingScrollPane)
        callbacks.customizeUiComponent(self._messageTable)
        callbacks.customizeUiComponent(self._CampaignTable)
        callbacks.customizeUiComponent(self._tabs)
        # callbacks.customizeUiComponent(buttons)

        # Handles checkbox color coding
        # Must be bellow the customizeUiComponent calls
        self._messageTable.setDefaultRenderer(
            Boolean, SuccessBooleanRenderer(self._db))

        # add the custom tab to Burp's UI
        callbacks.addSuiteTab(self)
        # register SendTo option
        callbacks.registerContextMenuFactory(self)

        return

    ##
    # implement ITab
    ##

    def getTabCaption(self):
        return "LightBulb"

    def getUiComponent(self):
        return self._splitpane

    ##
    # Creates the sendto tab in other areas of Burp
    ##

    def createMenuItems(self, invocation):
        messages = invocation.getSelectedMessages()

        def addRequestsToTab(e):
            for messageInfo in messages:
                parameters = self._helpers.analyzeRequest(
                    messageInfo.getRequest()).getParameters()
                # saveBuffers is required since modifying the original from its
                # source changes the saved objects, its not a copy
                messageIndex = self._db.createNewMessage(
                    self._callbacks.saveBuffersToTempFiles(messageInfo),
                    messageInfo.getHost(),
                    self._helpers.analyzeRequest(
                        messageInfo.getRequest()).getMethod(),
                    self._helpers.analyzeRequest(messageInfo).getUrl().getPath(),
                    parameters,
                    True)
                # self._messageTable.getModel().addRow(row)
            self._messageTable.redrawTable()

        ret = []
        menuItem = JMenuItem("Send request(s) to LightBulb")
        menuItem.addActionListener(addRequestsToTab)
        ret.append(menuItem)
        return(ret)

    ##
    # implement IMessageEditorController
    # this allows our request/response viewers to obtain details about the messages being displayed
    ##
    # TODO: Is this necessary? The request viewers may not require this since they aren't editable
    ##

    def getHttpService(self):
        return self._currentlyDisplayedItem.getHttpService()

    def getRequest(self):
        return self._currentlyDisplayedItem.getRequest()

    def getResponse(self):
        return self._currentlyDisplayedItem.getResponse()

    ##
    # Methods for running messages and analyzing results
    ##

    def runMessagesThread(self, indexes=None):
        print 'runMessagesThread'
        try:
            if not indexes:
                indexes = self._db.getActiveMessageIndexes()
            if isinstance(indexes, int):
                indexes = [indexes]
            for index in indexes:
                print 'processing new message'
                handlerconfig = {}
                handlerconfig['INDEX'] = index
                handlerconfig['PARAM'] = None
                handlerconfig['PARENT'] = self
                handlerconfig['CAMPAIGN'] = None
                handlerconfig['SHOW'] = "true"
                handlerconfig['ID'] = 1
                self.runMessage(handlerconfig)
        except:
            print 'error in runMessagesThread'
            print sys.exc_info()

    def LearningMessagesThread(self, indexes=None):
        print 'LearningMessagesThread'
        try:
            if not indexes:
                indexes = self._db.getActiveMessageIndexes()
            for index in indexes:
                configuration = self.prepare_learn({})
                if len(configuration) == 0:
                    die()
                if configuration["TESTS_FILE"] is None:
                    JOptionPane.showMessageDialog(
                        self._splitpane,
                        'Error, for GOFA algorithm, at least a TEST file must be selected',
                        "Error",
                        JOptionPane.INFORMATION_MESSAGE)
                    die()

                print 'configuration OK'
                campaignindex, targetparameter = self.CreateCampaign(index)
                print 'campaign OK'

                if self.findSetting('NATIVE', 'Learning').upper() == "TRUE":
                    message, host, method, path, \
                    targettype, success_regex, fail_regex, \
                    parameters, port, https \
                        = self.MembershipRequestsInit(index, targetparameter)
                    handlerconfig = {}
                    handlerconfig['MESSAGE'] = base64.b64encode(bytes(message))
                    handlerconfig['HOST'] = host.encode('ascii', 'ignore')
                    handlerconfig['PORT'] = port
                    handlerconfig['HTTPS'] = https
                    handlerconfig['BLOCK'] = fail_regex
                    handlerconfig['BYPASS'] = success_regex
                    handlerconfig['ECHO'] = "Handler_A_Membership"
                    print 'handlerconfig OK'

                    nativehandler = NativeHandler(campaignindex, self)

                    stats = self.lightbulbapp_native.start_gofa_algorithm(self.findSetting('NATIVE_PATH', 'Learning'), configuration, "RawHTTPHandler", handlerconfig, nativehandler.readline)
                else:
                    handlerconfig = {}
                    handlerconfig['INDEX'] = index
                    handlerconfig['PARAM'] = targetparameter
                    handlerconfig['PARENT'] = self
                    handlerconfig['CAMPAIGN'] = campaignindex
                    handlerconfig['SHOW'] = self.findSetting('SHOW', 'Learning')
                    handlerconfig['ID'] = 1
                    print 'handlerconfig OK'
                    stats = self.lightbulbapp.start_gofa_algorithm(configuration, BurpHTTPHandler, handlerconfig)
                print stats
                for stat in stats:
                    if stat[0] == 'Bypass' :
                        if stat[1] is None or  stat[1] == "None":
                            self.updateCampaign(
                                campaignindex, 'Not Found', stats)
                        else:
                            self.updateCampaign(
                                campaignindex, 'Bypassed', stats)
                        break
        except:
            print 'error in LearningMessagesThread'
            print sys.exc_info()

    def DiffLearningMessagesThread(self, indexes=None, param=None):
        print 'DiffLearningMessagesThread'
        try:
            if param == "WAF":
                if not indexes:
                    indexes = self._db.getActiveMessageIndexes()
                if len(indexes) > 2:
                    print 'Error, only two requests can be processed at a time'
                    JOptionPane.showMessageDialog(
                        self._splitpane,
                        'Error, only two requests can be processed at a time',
                        "Error",
                        JOptionPane.INFORMATION_MESSAGE)
                    die()

                configuration_A = self.prepare_learn({})
                if len(configuration_A) == 0:
                    die()
                print 'configuration_A OK'
                if configuration_A["SEED_FILE"] is None and configuration_A[
                        "TESTS_FILE"] is None:
                    JOptionPane.showMessageDialog(
                        self._splitpane,
                        'Error, for SFADiff algorithm, at least a SEED or a TEST file must be selected at Learning panel',
                        "Error",
                        JOptionPane.INFORMATION_MESSAGE)
                    die()

                configuration_B = self.prepare_learn({}, "SFADIFF")
                if len(configuration_B) == 0:
                    die()
                print 'configuration_B OK'
                if configuration_B["SEED_FILE"] is None and configuration_B[
                        "TESTS_FILE"] is None:
                    JOptionPane.showMessageDialog(
                        self._splitpane,
                        'Error, for SFADiff algorithm, at least a SEED or a TEST file must be selected at Differential Learning panel',
                        "Error",
                        JOptionPane.INFORMATION_MESSAGE)
                    die()
                configuration_A['DFA1_MINUS_DFA2'] = False
                configuration_B['DFA1_MINUS_DFA2'] = False
                campaignindex, targetparameter_A, targetparameter_B = self.CreateCampaignDiff(
                    indexes[0], indexes[1])
                print 'campaign OK'

                if self.findSetting('NATIVE', 'Learning').upper() == "TRUE":
                    message, host, method, path, \
                    targettype, success_regex, fail_regex, \
                    parameters, port, https \
                        = self.MembershipRequestsInit(indexes[0], targetparameter_A)
                    handlerconfig_A = {}
                    handlerconfig_A['MESSAGE'] = base64.b64encode(bytes(message))
                    handlerconfig_A['HOST'] = host
                    handlerconfig_A['PORT'] = port
                    handlerconfig_A['HTTPS'] = https
                    handlerconfig_A['BLOCK'] = fail_regex
                    handlerconfig_A['BYPASS'] = success_regex
                    handlerconfig_A['ECHO'] = "Handler_A_Membership"
                    print 'handlerconfig_A OK'
                    message, host, method, path, \
                    targettype, success_regex, fail_regex, \
                    parameters, port, https \
                        = self.MembershipRequestsInit(indexes[1], targetparameter_B)
                    handlerconfig_B = {}
                    handlerconfig_B['MESSAGE'] = base64.b64encode(bytes(message))
                    handlerconfig_B['HOST'] = host.encode('ascii', 'ignore')
                    handlerconfig_B['PORT'] = port
                    handlerconfig_B['HTTPS'] = https
                    handlerconfig_B['BLOCK'] = fail_regex
                    handlerconfig_B['BYPASS'] = success_regex
                    handlerconfig_B['ECHO'] = "Handler_B_Membership"
                    print 'handlerconfig_B OK'

                    nativehandler = NativeHandler(campaignindex, self)

                    stats = self.lightbulbapp_native.start_sfadiff_algorithm(
                        self.findSetting('NATIVE_PATH', 'Learning'),
                        configuration_A,
                        configuration_B,
                        handlerconfig_A,
                        handlerconfig_B,
                        "RawHTTPHandler",
                        "RawHTTPHandler",
                        nativehandler.readline)
                else:
                    handlerconfig_A = {}
                    handlerconfig_A['INDEX'] = indexes[0]
                    handlerconfig_A['PARAM'] = targetparameter_A
                    handlerconfig_A['PARENT'] = self
                    handlerconfig_A['CAMPAIGN'] = campaignindex
                    handlerconfig_A['SHOW'] = self.findSetting('SHOW', 'Learning')
                    handlerconfig_A['ID'] = 2
                    print 'handlerconfig_A OK'

                    handlerconfig_B = {}
                    handlerconfig_B['INDEX'] = indexes[1]
                    handlerconfig_B['PARAM'] = targetparameter_B
                    handlerconfig_B['PARENT'] = self
                    handlerconfig_B['CAMPAIGN'] = campaignindex
                    handlerconfig_B['SHOW'] = self.findSetting('SHOW', 'Learning')
                    handlerconfig_B['ID'] = 1
                    print 'handlerconfig_A OK'

                    stats = self.lightbulbapp.start_sfadiff_algorithm(
                        configuration_A,
                        configuration_B,
                        handlerconfig_A,
                        handlerconfig_B,
                        BurpHTTPHandler,
                        BurpHTTPHandler)
                for stat in stats:
                    if stat[0] == 'Bypass':
                        if stat[1] is None or  stat[1] == "None":
                            self.updateCampaign(
                                campaignindex, 'Not Found', stats)
                        else:
                            self.updateCampaign(
                                campaignindex, 'Bypassed', stats)
                        break

            elif param == "Browser":
                if not indexes:
                    indexes = self._db.getActiveMessageIndexes()
                for index in indexes:
                    configuration_A = self.prepare_learn({})
                    if len(configuration_A) == 0:
                        die()
                    print 'configuration_A OK'
                    if configuration_A["SEED_FILE"] is None and configuration_A[
                            "TESTS_FILE"] is None:
                        JOptionPane.showMessageDialog(
                            self._splitpane,
                            'Error, for SFADiff algorithm, at least a SEED or a TEST file must be selected at Learning panel',
                            "Error",
                            JOptionPane.INFORMATION_MESSAGE)
                        die()

                    configuration_B = self.prepare_learn({}, "SFADIFF")
                    if len(configuration_B) == 0:
                        die()
                    print 'configuration_B OK'
                    if configuration_B["SEED_FILE"] is None and configuration_B[
                            "TESTS_FILE"] is None:
                        JOptionPane.showMessageDialog(
                            self._splitpane,
                            'Error, for SFADiff algorithm, at least a SEED or a TEST file must be selected at Differential Learning panel',
                            "Error",
                            JOptionPane.INFORMATION_MESSAGE)
                        die()
                    configuration_A['DFA1_MINUS_DFA2'] = True
                    configuration_B['DFA1_MINUS_DFA2'] = True
                    campaignindex, targetparameter = self.CreateCampaign(index)
                    print 'campaign OK'

                    if self.findSetting('NATIVE', 'Learning').upper() == "TRUE":
                        message, host, method, path, \
                        targettype, success_regex, fail_regex, \
                        parameters, port, https \
                            = self.MembershipRequestsInit(index, targetparameter)
                        handlerconfig_A = {}
                        handlerconfig_A = self.prepare_browser({})
                        handlerconfig_A['ECHO'] = "Handler_B_Membership"
                        print 'handlerconfig_A OK'
                        message, host, method, path, \
                        targettype, success_regex, fail_regex, \
                        parameters, port, https \
                            = self.MembershipRequestsInit(index, targetparameter)
                        handlerconfig_B = {}
                        handlerconfig_B['MESSAGE'] = base64.b64encode(bytes(message))
                        handlerconfig_B['HOST'] = host.encode('ascii', 'ignore')
                        handlerconfig_B['PORT'] = port
                        handlerconfig_B['HTTPS'] = https
                        handlerconfig_B['BLOCK'] = fail_regex
                        handlerconfig_B['BYPASS'] = success_regex
                        handlerconfig_B['ECHO'] = "Handler_A_Membership"
                        print 'handlerconfig_B OK'

                        nativehandler = NativeHandler(campaignindex, self)

                        stats = self.lightbulbapp_native.start_sfadiff_algorithm(
                            self.findSetting('NATIVE_PATH', 'Learning'),
                            configuration_A,
                            configuration_B,
                            handlerconfig_A,
                            handlerconfig_B,
                            "BrowserHandler",
                            "RawHTTPHandler",
                            nativehandler.readline)
                    else:
                        handlerconfig_A = {}
                        handlerconfig_A = self.prepare_browser({})
                        handlerconfig_A['PARENT'] = self
                        handlerconfig_A['CAMPAIGN'] = campaignindex
                        handlerconfig_A['ID'] = 2
                        print 'handlerconfig_A OK'

                        handlerconfig_B = {}
                        handlerconfig_B['INDEX'] = index
                        handlerconfig_B['PARAM'] = targetparameter
                        handlerconfig_B['PARENT'] = self
                        handlerconfig_B['CAMPAIGN'] = campaignindex
                        handlerconfig_B['SHOW'] = self.findSetting(
                            'SHOW', 'Learning')
                        handlerconfig_B['ID'] = 1
                        print 'handlerconfig_B OK'

                        stats = self.lightbulbapp.start_sfadiff_algorithm(
                            configuration_A,
                            configuration_B,
                            handlerconfig_A,
                            handlerconfig_B,
                            BurpBrowserHandler,
                            BurpHTTPHandler)
                    for stat in stats:
                        if stat[0] == 'Bypass':
                            if stat[1] is None or  stat[1] == "None":
                                self.updateCampaign(
                                    campaignindex, 'Not Found', stats)
                            else:
                                self.updateCampaign(
                                    campaignindex, 'Bypassed', stats)
                            break
            elif param == "BrowserFilter":
                if not indexes:
                    indexes = self._db.getActiveMessageIndexes()
                for index in indexes:
                    configuration_A = self.prepare_learn({})
                    if len(configuration_A) == 0:
                        die()
                    print 'configuration_A OK'
                    if configuration_A["SEED_FILE"] is None and configuration_A[
                            "TESTS_FILE"] is None:
                        JOptionPane.showMessageDialog(
                            self._splitpane,
                            'Error, for SFADiff algorithm, at least a SEED or a TEST file must be selected at Learning panel',
                            "Error",
                            JOptionPane.INFORMATION_MESSAGE)
                        die()

                    configuration_B = self.prepare_learn({}, "SFADIFF")
                    if len(configuration_B) == 0:
                        die()
                    print 'configuration_B OK'
                    if configuration_B["SEED_FILE"] is None and configuration_B[
                            "TESTS_FILE"] is None:
                        JOptionPane.showMessageDialog(
                            self._splitpane,
                            'Error, for SFADiff algorithm, at least a SEED or a TEST file must be selected at Differential Learning panel',
                            "Error",
                            JOptionPane.INFORMATION_MESSAGE)
                        die()
                    configuration_A['DFA1_MINUS_DFA2'] = True
                    configuration_B['DFA1_MINUS_DFA2'] = True
                    campaignindex, targetparameter = self.CreateCampaign(index)
                    print 'campaign OK'


                    if self.findSetting('NATIVE', 'Learning').upper() == "TRUE":
                        message, host, method, path, \
                        targettype, success_regex, fail_regex, \
                        parameters, port, https \
                            = self.MembershipRequestsInit(index, targetparameter)
                        handlerconfig_A = {}
                        handlerconfig_A = self.prepare_browser({})
                        handlerconfig_A['ECHO'] = "Handler_B_Membership"
                        print 'handlerconfig_A OK'
                        message, host, method, path, \
                        targettype, success_regex, fail_regex, \
                        parameters, port, https \
                            = self.MembershipRequestsInit(index, targetparameter)
                        handlerconfig_B = {}
                        handlerconfig_B['MESSAGE'] = base64.b64encode(bytes(message))
                        handlerconfig_B['HOST'] = host.encode('ascii', 'ignore')
                        handlerconfig_B['PORT'] = port
                        handlerconfig_B['HTTPS'] = https
                        handlerconfig_B['BLOCK'] = fail_regex
                        handlerconfig_B['BYPASS'] = success_regex
                        handlerconfig_B['ECHO'] = "Handler_A_Membership"
                        print 'handlerconfig_B OK'

                        nativehandler = NativeHandler(campaignindex, self)

                        stats = self.lightbulbapp_native.start_sfadiff_algorithm(
                            self.findSetting('NATIVE_PATH', 'Learning'),
                            configuration_A,
                            configuration_B,
                            handlerconfig_A,
                            handlerconfig_B,
                            "BrowserFilterHandler",
                            "RawHTTPHandler",
                            nativehandler.readline)
                    else:
                        handlerconfig_A = {}
                        handlerconfig_A = self.prepare_browser({})
                        handlerconfig_A['PARENT'] = self
                        handlerconfig_A['CAMPAIGN'] = campaignindex
                        handlerconfig_A['ID'] = 2
                        print 'handlerconfig_A OK'


                        handlerconfig_B = {}
                        handlerconfig_B['INDEX'] = index
                        handlerconfig_B['PARAM'] = targetparameter
                        handlerconfig_B['PARENT'] = self
                        handlerconfig_B['CAMPAIGN'] = campaignindex
                        handlerconfig_B['SHOW'] = self.findSetting(
                            'SHOW', 'Learning')
                        handlerconfig_B['ID'] = 1
                        print 'handlerconfig_B OK'

                        stats = self.lightbulbapp.start_sfadiff_algorithm(
                            configuration_A,
                            configuration_B,
                            handlerconfig_A,
                            handlerconfig_B,
                            BurpBrowserFilterHandler,
                            BurpHTTPHandler)
                    for stat in stats:
                        if stat[0] == 'Bypass':
                            if stat[1] is None or  stat[1] == "None":
                                self.updateCampaign(
                                    campaignindex, 'Not Found', stats)
                            else:
                                self.updateCampaign(
                                    campaignindex, 'Bypassed', stats)
                            break
            elif param == "MySQL":
                if not indexes:
                    indexes = self._db.getActiveMessageIndexes()
                for index in indexes:
                    configuration_A = self.prepare_learn({})
                    if len(configuration_A) == 0:
                        die()
                    print 'configuration_A OK'
                    if configuration_A["SEED_FILE"] is None and configuration_A[
                            "TESTS_FILE"] is None:
                        JOptionPane.showMessageDialog(
                            self._splitpane,
                            'Error, for SFADiff algorithm, at least a SEED or a TEST file must be selected at Learning panel',
                            "Error",
                            JOptionPane.INFORMATION_MESSAGE)
                        die()

                    configuration_B = self.prepare_learn({}, "SFADIFF")
                    if len(configuration_B) == 0:
                        die()
                    print 'configuration_B OK'
                    if configuration_B["SEED_FILE"] is None and configuration_B[
                            "TESTS_FILE"] is None:
                        JOptionPane.showMessageDialog(
                            self._splitpane,
                            'Error, for SFADiff algorithm, at least a SEED or a TEST file must be selected at Differential Learning panel',
                            "Error",
                            JOptionPane.INFORMATION_MESSAGE)
                        die()
                    configuration_A['DFA1_MINUS_DFA2'] = True
                    configuration_B['DFA1_MINUS_DFA2'] = True

                    campaignindex, targetparameter = self.CreateCampaign(index)
                    print 'campaign OK'


                    if self.findSetting('NATIVE', 'Learning').upper() == "TRUE":
                        message, host, method, path, \
                        targettype, success_regex, fail_regex, \
                        parameters, port, https \
                            = self.MembershipRequestsInit(index, targetparameter)
                        handlerconfig_A = {}
                        handlerconfig_A = self.prepare_mysql({})
                        handlerconfig_A['ECHO'] = "Handler_B_Membership"
                        print 'handlerconfig_A OK'
                        message, host, method, path, \
                        targettype, success_regex, fail_regex, \
                        parameters, port, https \
                            = self.MembershipRequestsInit(index, targetparameter)
                        handlerconfig_B = {}
                        handlerconfig_B['MESSAGE'] = base64.b64encode(bytes(message))
                        handlerconfig_B['HOST'] = host.encode('ascii', 'ignore')
                        handlerconfig_B['PORT'] = port
                        handlerconfig_B['HTTPS'] = https
                        handlerconfig_B['BLOCK'] = fail_regex
                        handlerconfig_B['BYPASS'] = success_regex
                        handlerconfig_B['ECHO'] = "Handler_A_Membership"
                        print 'handlerconfig_B OK'

                        nativehandler = NativeHandler(campaignindex, self)

                        stats = self.lightbulbapp_native.start_sfadiff_algorithm(
                            self.findSetting('NATIVE_PATH', 'Learning'),
                            configuration_A,
                            configuration_B,
                            handlerconfig_A,
                            handlerconfig_B,
                            "SQLHandler",
                            "RawHTTPHandler",
                            nativehandler.readline)
                    else:
                        handlerconfig_A = {}
                        handlerconfig_A = self.prepare_mysql({})
                        handlerconfig_A['PARENT'] = self
                        handlerconfig_A['CAMPAIGN'] = campaignindex
                        handlerconfig_A['ID'] = 2
                        print 'handlerconfig_A OK'

                        handlerconfig_B = {}
                        handlerconfig_B['INDEX'] = index
                        handlerconfig_B['PARAM'] = targetparameter
                        handlerconfig_B['PARENT'] = self
                        handlerconfig_B['CAMPAIGN'] = campaignindex
                        handlerconfig_B['SHOW'] = self.findSetting(
                            'SHOW', 'Learning')
                        handlerconfig_B['ID'] = 1
                        print 'handlerconfig_A OK'

                        stats = self.lightbulbapp.start_sfadiff_algorithm(
                            configuration_A,
                            configuration_B,
                            handlerconfig_A,
                            handlerconfig_B,
                            BurpSQLHandler,
                            BurpHTTPHandler)
                    for stat in stats:
                        if stat[0] == 'Bypass':
                            if stat[1] is None or  stat[1] == "None":
                                self.updateCampaign(
                                    campaignindex, 'Not Found', stats)
                            else:
                                self.updateCampaign(
                                    campaignindex, 'Bypassed', stats)
                            break
            elif param == "BrowserBrowser":
                configuration_A = self.prepare_learn({})
                if len(configuration_A) == 0:
                    die()
                print 'configuration_A OK'
                if configuration_A["SEED_FILE"] is None and configuration_A[
                        "TESTS_FILE"] is None:
                    JOptionPane.showMessageDialog(
                        self._splitpane,
                        'Error, for SFADiff algorithm, at least a SEED or a TEST file must be selected at Learning panel',
                        "Error",
                        JOptionPane.INFORMATION_MESSAGE)
                    die()

                configuration_B = self.prepare_learn({}, "SFADIFF")
                if len(configuration_B) == 0:
                    die()
                print 'configuration_B OK'
                if configuration_B["SEED_FILE"] is None and configuration_B[
                        "TESTS_FILE"] is None:
                    JOptionPane.showMessageDialog(
                        self._splitpane,
                        'Error, for SFADiff algorithm, at least a SEED or a TEST file must be selected at Differential Learning panel',
                        "Error",
                        JOptionPane.INFORMATION_MESSAGE)
                    die()
                configuration_A['DFA1_MINUS_DFA2'] = False
                configuration_B['DFA1_MINUS_DFA2'] = False
                campaignindex, targetparameter = self.CreateCampaign(-1)
                print 'campaign OK'

                handlerconfig_A = {}
                handlerconfig_A = self.prepare_browser({})
                handlerconfig_A['PARENT'] = self
                handlerconfig_A['CAMPAIGN'] = campaignindex
                handlerconfig_A['ID'] = 2
                print 'handlerconfig_A OK'

                handlerconfig_B = {}
                handlerconfig_B = self.prepare_browser({})
                handlerconfig_B['PARENT'] = self
                handlerconfig_B['CAMPAIGN'] = campaignindex
                handlerconfig_B['ID'] = 1
                print 'handlerconfig_A OK'

                if self.findSetting('NATIVE', 'Learning').upper() == "TRUE":

                    handlerconfig_A['ECHO'] = "Handler_A_Membership"
                    handlerconfig_B['ECHO'] = "Handler_B_Membership"
                    nativehandler = NativeHandler(campaignindex, self)

                    stats = self.lightbulbapp_native.start_sfadiff_algorithm(
                        self.findSetting('NATIVE_PATH', 'Learning'),
                        configuration_A,
                        configuration_B,
                        handlerconfig_A,
                        handlerconfig_B,
                        "BrowserHandler",
                        "BrowserHandler",
                        nativehandler.readline)
                else:



                    stats = self.lightbulbapp.start_sfadiff_algorithm(
                        configuration_A,
                        configuration_B,
                        handlerconfig_A,
                        handlerconfig_B,
                        BurpBrowserHandler,
                        BurpBrowserHandler)
                for stat in stats:
                    if stat[0] == 'Bypass':
                        if stat[1] is None or  stat[1] == "None":
                            self.updateCampaign(
                                campaignindex, 'Not Found', stats)
                        else:
                            self.updateCampaign(
                                campaignindex, 'Bypassed', stats)
                        break
        except:
            print 'error in DiffLearningMessagesThread'
            print sys.exc_info()

    def DistinguishThread(self, indexes=None):
        print 'DistinguishThread'
        try:
            if not indexes:
                indexes = self._db.getActiveMessageIndexes()
            for index in indexes:
                configuration = self.prepare_distinguish({})
                if len(configuration) == 0:
                    die()
                print 'configuration OK'
                campaignindex, targetparameter = self.CreateCampaign(index)
                print 'campaign OK'
                handlerconfig = {}
                handlerconfig['INDEX'] = index
                handlerconfig['PARAM'] = targetparameter
                handlerconfig['PARENT'] = self
                handlerconfig['CAMPAIGN'] = campaignindex
                handlerconfig['SHOW'] = self.findSetting('SHOW', 'Learning')
                handlerconfig['ID'] = 1
                print 'handlerconfig OK'
                stats = self.lightbulbapp.start_distinguishing_module(
                    configuration, BurpHTTPHandler, handlerconfig)
                self.updateCampaign(campaignindex, 'Finished', stats)
        except:
            print 'error in DistinguishThread'
            print sys.exc_info()

    def TreeGenThread(self, indexes=None):
        print 'DistinguishTreeThread'
        try:
            if not indexes:
                indexes = self._db.getActiveMessageIndexes()
            configuration = {}
            configuration = self.prepare_gen({})
            print 'configuration OK'
            if len(configuration) == 0:
                die()
            campaignindex = self.CreateCampaignThread(
                configuration['FILE_OUT'])
            wafs = {}
            for index in indexes:
                wafkey = index
                paramVal = JOptionPane.showInputDialog(
                    self._splitpane,
                    "Please type the name of the WAF that can be accessed using the HTTP request #" +
                    repr(index),
                    "Tree Generation Attributes",
                    JOptionPane.QUESTION_MESSAGE)
                while not paramVal or len(paramVal) == 0:
                    JOptionPane.showMessageDialog(
                        self._splitpane,
                        'Error, the name was empty',
                        "Error",
                        JOptionPane.INFORMATION_MESSAGE)
                    paramVal = JOptionPane.showInputDialog(
                        self._splitpane,
                        "Please type the name of the WAF that can be accessed using the HTTP request #" +
                        repr(index),
                        "Tree Generation Attributes",
                        JOptionPane.QUESTION_MESSAGE)
                wafs[wafkey] = {}
                wafs[wafkey]['name'] = paramVal
                messageEntry = self._db.arrayOfMessages[index]
                data = []
                if len(messageEntry._selectedparameter) == 0:
                    JOptionPane.showMessageDialog(
                        self._splitpane,
                        'Error, please select a request with at least one parameter',
                        "Error",
                        JOptionPane.INFORMATION_MESSAGE)
                    die()
                for param in messageEntry._selectedparameter:
                    data.append(param.getName())
                paramVal = None
                if len(data) > 0:
                    paramVal = JOptionPane.showInputDialog(
                        self._splitpane,
                        "Please choose parameter to use as testing input",
                        "Learning Attributes",
                        JOptionPane.QUESTION_MESSAGE,
                        None,
                        tuple(data),
                        data[
                            -1])
                    if not paramVal is None:
                        targetparameter = paramVal
                handlerconfig = {}
                handlerconfig['INDEX'] = index
                handlerconfig['PARAM'] = targetparameter
                handlerconfig['PARENT'] = self
                handlerconfig['CAMPAIGN'] = campaignindex
                handlerconfig['SHOW'] = self.findSetting('SHOW', 'Learning')
                handlerconfig['ID'] = 1
                wafs[wafkey]['HANDLER'] = BurpHTTPHandler(handlerconfig)
            print 'handlerconfig OK'
            configuration['WAFS'] = wafs

            name = configuration['FILE_OUT']
            data = "changeddata"
            category = "trees"
            extension = ".json"
            categorytype = "Tree"
            specialcat = "my_saved_trees"

            home = expanduser("~")
            timestr = time.strftime("%Y%m%d-%H%M%S")
            if not os.path.exists(home + "/.LightBulb/"):
                os.makedirs(home + "/.LightBulb/")
            if not os.path.exists(home + "/.LightBulb/" + category):
                os.makedirs(home + "/.LightBulb/" + category)

            if os.path.exists(home + "/.LightBulb/" + category + "/" + name + ".py"):
                JOptionPane.showMessageDialog(
                    self._splitpane,
                    'File already exists. Please choose a different name',
                    "Error",
                    JOptionPane.INFORMATION_MESSAGE)
                return
            configuration['FILE_OUT'] = home + "/.LightBulb/" + category + "/" + name + extension
            stats = self.lightbulbapp.start_treegeneration_module(
                configuration)
            self.updateCampaign(campaignindex, 'Finished', stats)


            ruleset_file_meta = open(
                home + "/.LightBulb/" + category + "/" + name + ".py", "w")
            ruleset_file_meta.write(
                "META = {\n\
                        'author': '" + getpass.getuser() + "',\n\
                        'description': 'Saved tree on " + timestr + "',\n\
                        'type':'" + categorytype + "',\n\
                        'comments': []\n\
                }")
            ruleset_file_meta.close()
            print "Saved Model", home + "/.LightBulb/" + category + "/" + name + ".py"
            print specialcat + "/" + name, False, categorytype, 'Saved model on ' + timestr, specialcat + "/" + name
            self._db.addSetting(
                specialcat + "/" + name,
                False,
                categorytype,
                'Saved tree on ' + timestr,
                specialcat + "/" + name)
            self.libraryredraw.redraw()
            ### End Saving ###
        except:
            print 'error in DistinguishTreeThread'
            print sys.exc_info()

    def CreateCampaign(self, index):
        if index >= 0:
            messageEntry = self._db.arrayOfMessages[index]
            data = []
            if len(messageEntry._selectedparameter) == 0:
                JOptionPane.showMessageDialog(
                    self._splitpane,
                    'Error, please select a request with at least one parameter',
                    "Error",
                    JOptionPane.INFORMATION_MESSAGE)
                die()
            for param in messageEntry._selectedparameter:
                data.append(param.getName())
            if len(data) > 0:
                paramVal = JOptionPane.showInputDialog(
                    self._splitpane,
                    "Please choose parameter to use as testing input",
                    "Learning Attributes",
                    JOptionPane.QUESTION_MESSAGE,
                    None,
                    tuple(data),
                    data[
                        -1])
                if not paramVal is None:
                    campaignindex = self._db.addCampaign(paramVal)
                    self._CampaignTable.redrawTable()
                    return campaignindex, paramVal
        else:
            campaignindex = self._db.addCampaign("Browser Browser")
            self._CampaignTable.redrawTable()
            return campaignindex, None

    def CreateCampaignThread(self, name):
        campaignindex = self._db.addCampaign(name)
        self._CampaignTable.redrawTable()
        return campaignindex

    def CreateCampaignDiff(self, index_A, index_B):
        messageEntry_A = self._db.arrayOfMessages[index_A]
        messageEntry_B = self._db.arrayOfMessages[index_B]
        data_A = []
        if len(messageEntry_A._selectedparameter) == 0:
            JOptionPane.showMessageDialog(
                self._splitpane,
                'Error, please select a request with at least one parameter',
                "Error",
                JOptionPane.INFORMATION_MESSAGE)
            die()
        if len(messageEntry_B._selectedparameter) == 0:
            JOptionPane.showMessageDialog(
                self._splitpane,
                'Error, please select a request with at least one parameter',
                "Error",
                JOptionPane.INFORMATION_MESSAGE)
            die()
        for param in messageEntry_A._selectedparameter:
            data_A.append(param.getName())
        data_B = []
        for param in messageEntry_B._selectedparameter:
            data_B.append(param.getName())
        if len(data_A) > 0 and len(data_B) > 0:
            paramVal_A = JOptionPane.showInputDialog(
                self._splitpane,
                "Please choose parameter to use as testing input for the first HTTP request",
                "Learning Attributes",
                JOptionPane.QUESTION_MESSAGE,
                None,
                tuple(data_A),
                data_A[
                    -1])
            paramVal_B = JOptionPane.showInputDialog(
                self._splitpane,
                "Please choose parameter to use as testing input for the second HTTP request",
                "Learning Attributes",
                JOptionPane.QUESTION_MESSAGE,
                None,
                tuple(data_B),
                data_B[
                    -1])

            if not paramVal_A is None and not paramVal_B is None:
                campaignindex = self._db.addCampaign(
                    paramVal_A + ', ' + paramVal_B)
                self._CampaignTable.redrawTable()
                return campaignindex, paramVal_A, paramVal_B


    def handleUpdateCampaign(self, campaign, id, membershiprequests):
        """
        The function performs an update in Burp Extension GUI about
        the total number of membership requests that have been made
        until now.
        Args:
            None
        Returns:
            None
        """
        try:
            if campaign is not None:
                self._db.updateCampaign(campaign, id, membershiprequests)
                self._CampaignTable.redrawTable()
        except:
            pass

    def updateCampaign(self, campaign, result, stats):
        self._db.arrayOfCampaigns[campaign]._Result = result
        self._db.arrayOfCampaigns[campaign]._Stats = stats
        self._CampaignTable.redrawTable()

    def updateCampaignObjects(self, campaign, inputlist):
        self._db.arrayOfCampaigns[campaign]._inputlist = inputlist

    def MembershipRequestsInit(self, messageIndex, targetparameter):
        messageEntry = self._db.arrayOfMessages[messageIndex]
        success_regex = messageEntry._successRegex
        fail_regex = messageEntry._failRegex
        host = messageEntry._host
        method = messageEntry._method
        path = messageEntry._name
        parameters = messageEntry._selectedparameter
        messageInfo = messageEntry._requestResponse
        # print 'parameters'
        targettype = None
        if targetparameter:
            for p in parameters:
                print p.getName()
                if p.getName() == targetparameter:
                    targettype = p.getType()
                    break
        print 'finish membership init'
        message =  self.prepareMembershipRequest(messageInfo, targetparameter, targettype, "--LIGHTBULB--REPLACE--HERE--").tostring()
        return message, host, method, path, targettype, success_regex, fail_regex, parameters, messageInfo.getPort(), messageInfo.getProtocol().find("https") > -1


    def prepareMembershipRequest(self, messageInfo,targetparameter, targettype, newvalue):
        request = messageInfo.getRequest()
        newreq = request
        if targetparameter and newvalue:
            np = self._helpers.buildParameter(
                targetparameter, newvalue, targettype)
            newreq = self._helpers.updateParameter(request, np)
        return newreq

    # TODO: This method is too large. Fix that
    def updateMembershipRequest(
            self,
            messageIndex,
            host,
            method,
            path,
            targetparameter,
            newvalue,
            success_regex,
            fail_regex,
            oldparameters,
            newreq,
            data,
            found):

        try:
            rq = myRequestResponse()
            rq.setRequest(newreq)
            rq.setResponse(data)

            if targetparameter and newvalue:
                newmessageIndex = self._db.createNewMessage(
                    rq, host, method, path, oldparameters, False, success_regex, fail_regex)
                newmessageEntry = self._db.arrayOfMessages[newmessageIndex]
            else:
                newmessageEntry = self._db.arrayOfMessages[messageIndex]

            if not found:
                newmessageEntry._successStatus = True
            else:
                newmessageEntry._successStatus = False

            self._messageTable.redrawTable()
        except:
            print 'error when updating membership request'
            print sys.exc_info()
        return found

    # TODO: This method is too large. Fix that
    def runMessage(self, handlerconfig):
        try:
            membership = BurpHTTPHandler(handlerconfig)
            membership.query(None)
        except:
            print sys.exc_info()
