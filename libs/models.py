"""
This file contains all the in-memory Database implementation
of the Burp Extension. The contained models are used for
maintaining the Burp Proxy requests and responses, the lightbulb's
filters (regexes, grammars), the lightbulb's trees, the user's
campaigns, and other info. The models also include all the
necessary functionality for representing the data to the end user
through Jython swing framework.
"""
from java.util import ArrayList
from java.lang import Boolean
from javax.swing import JTabbedPane
from javax.swing import JTable
from javax.swing import JCheckBox
from javax.swing import JLabel
from javax.swing.table import AbstractTableModel
from javax.swing.table import TableCellRenderer
from threading import Lock
from threading import Thread
import sys

class BurpDatabaseModels():
    """
    The in-memory Database implementation
    of the Burp Extension.
    """

    def __init__(self):
        """
        The constructor of BurpDatabaseModels object defines a number of
        class variables tracking the number of deleted records, and maintaining
        the references to the arrays of records.
        Args:
            None
        Returns:
            None
        """

        self.STATIC_MESSAGE_TABLE_COLUMN_COUNT = 6
        self.lock = Lock()
        self.arrayOfMessages = ArrayList()
        self.arrayOfCampaigns = ArrayList()
        self.arrayOfSettings = ArrayList()
        self.deletedCampaignCount = 0
        self.deletedRoleCount = 0
        self.deletedMessageCount = 0
        self.deletedSettingCount = 0
        self.selfExtender = None

    def addCampaign(self, name):
        """
        Adds a new record in the Campaigns array,
        and returns the index of the campaign.
        Args:
            name (str): The name of the campaign
        Returns:
            int: The index of the inserted campaign
        """
        campaign_index = -1
        try:
            self.lock.acquire()
            campaign_index = self.arrayOfCampaigns.size()
            self.arrayOfCampaigns.append(
                CampaignEntry(
                    campaign_index,
                    campaign_index - self.deletedCampaignCount,
                    name))
        finally:
            self.lock.release()
        return campaign_index


    def updateCampaign(self, campaign_index, id, val):
        """
        Adds a new record in the Campaigns array,
        and returns the index of the campaign.
        Args:
            name (str): The name of the campaign
        Returns:
            int: The index of the inserted campaign
        """
        try:
            self.lock.acquire()
            campaign_entry = self.arrayOfCampaigns[campaign_index]
            if campaign_entry:
                if id == 1:
                    campaign_entry._Membership = val
                if id == 2:
                    campaign_entry._MembershipB = val
        except:
            print 'Error when inserting campaings. Wanted to insert campaign with id ',campaign_index
            size = self.arrayOfCampaigns.size()
            print 'Current campaigns:',size
            for i in self.arrayOfCampaigns:
                print 'Campaign with id ',i._index
            print sys.exc_info()

        finally:
            self.lock.release()

    def delete_campaign(self, campaignIndex):
        """
        Delete the selected row of the campaigns
        Args:
            row (str): The row of the table that the campaign appears
        Returns:
            None
        """
        try:
            self.lock.acquire()
            print 'Terminating Campaign'
            campaign_entry = self.arrayOfCampaigns[campaignIndex]
            if campaign_entry:
                campaign_entry._deleted = True
                campaign_entry._Result = "Terminated"
                self.deletedCampaignCount += 1
                if len(self.arrayOfCampaigns) > campaignIndex + 1:
                    for i in self.arrayOfCampaigns[campaignIndex + 1:]:
                        i._tableRow -= 1
            print 'Campaign was Terminated'
        finally:
            self.lock.release()

    def addSetting(self, name, value, domain=None,
                   description=None, path=None):
        """
        Adds a new record in the settings array,
        and returns the index of the setting.
        Args:
            name (str): The name of the setting
            value (str): The value of the setting
            domain (str): The category of the setting (optional)
            description (str): A small description of the setting (optional)
            path (str): The location of the described resource (optional)
        Returns:
            int: The index of the inserted setting
        """
        self.lock.acquire()
        settingIndex = -1
        for i in self.getActiveSettingIndexes(domain):

            if self.arrayOfSettings[i]._name == name:
                settingIndex = i
        if settingIndex < 0:
            settingIndex = self.arrayOfSettings.size()
            self.arrayOfSettings.append(
                SettingEntry(
                    settingIndex, len(
                        self.getActiveSettingIndexes(domain)), name, value, domain, description, path))

        self.lock.release()
        return settingIndex

    def createNewMessage(
            self,
            messagebuffer,
            host,
            method,
            path,
            selectedparameter,
            totest=False,
            regex="HTTP/1.1 200 OK",
            failRegex="(HTTP/1.1 403|block|impact)"):
        """
        Adds a new record in the messages array,
        and returns the index of the message.
        Args:
            messagebuffer (str): The saved buffer of the burp request-response
            host (str): The targetted host
            method (str): The used HTTP method
            path (str): The HTTP URL path
            selectedparameter (str): The parameter of the HTTP request
            totest (bool): A boolean vaule indicating weather to test with the regex
            the response or not
            regex (str): A regex that if matches the response indicates a success
            failRegex (str): A regex that if matches the response indicates a failure
        Returns:
            int: The index of the inserted message
        """
        self.lock.acquire()
        messageIndex = self.arrayOfMessages.size()
        self.arrayOfMessages.add(
            MessageEntry(
                messageIndex,
                messageIndex -
                self.deletedMessageCount,
                messagebuffer,
                host,
                method,
                path,
                selectedparameter,
                regex,
                failRegex))
        self.lock.release()
        if totest:
            t = Thread(
                target=self.selfExtender.runMessagesThread,
                args=[messageIndex])
            t.start()
        return messageIndex

    def clear(self):
        """
        Clears all arrays and all counters
        Args:
            None
        Returns:
            None
        """
        self.lock.acquire()
        self.arrayOfMessages = ArrayList()
        self.arrayOfCampaigns = ArrayList()
        self.deletedCampaignCount = 0
        self.deletedRoleCount = 0
        self.deletedMessageCount = 0
        self.lock.release()

    def getActiveCampaignIndexes(self):
        """
        Gets all campaigns that are not deleted
        Args:
            None
        Returns:
            array: The active campaigns
        """
        return [x._index for x in self.arrayOfCampaigns if not x.isDeleted()]

    def getActiveMessageIndexes(self):
        """
        Gets all messages that are not deleted
        Args:
            None
        Returns:
            array: The active messages
        """
        return [x._index for x in self.arrayOfMessages if not x.isDeleted()]

    def getActiveSettingIndexes(self, domain=None):
        """
        Gets all settings that are not deleted and belong to the input category
        Args:
            domain (str): The category of the requested settings (optional)
        Returns:
            array: The returned settings
        """
        return [
            x._index for x in self.arrayOfSettings if not x.isDeleted() and (
                not domain or x._domain == domain)]

    def getMessageByRow(self, row):
        """
        Gets a selected row of the messages, as long as it is not deleted.
        Args:
            row (str): The row of the table that the message appears
        Returns:
            array: The returned row with the message details
        """
        for m in self.arrayOfMessages:
            if not m.isDeleted() and m.getTableRow() == row:
                return m

    def getSettingByRow(self, row, domain=None):
        """
        Gets the a selected row of the settings, as long as it is not deleted.
        Args:
            row (str): The row of the table that the message appears
        Returns:
            array: The returned row with the setting details
        """
        for m in [
            x for x in self.arrayOfSettings if (
                not domain or x._domain == domain)]:
            if not m.isDeleted() and m.getTableRow() == row and (
                    not domain or m._domain == domain):
                return m

    def getCampaignByRow(self, row):
        """
        Gets the a selected row of the campaigns, as long as it is not deleted.
        Args:
            row (str): The row of the table that the message appears
        Returns:
            array: The returned row with the campaign details
        """
        for u in self.arrayOfCampaigns:
            if not u.isDeleted() and u.getTableRow() == row:
                return u


    def delete_message(self, messageIndex):
        """
        Delete the selected row of the messages
        Args:
            row (str): The row of the table that the message appears
        Returns:
            None
        """
        self.lock.acquire()
        messageEntry = self.arrayOfMessages[messageIndex]
        if messageEntry:
            messageEntry._deleted = True
            self.deletedMessageCount += 1
            if len(self.arrayOfMessages) > messageIndex + 1:
                for i in self.arrayOfMessages[messageIndex + 1:]:
                    i._tableRow -= 1
        self.lock.release()


"""
Swing Table Modles
"""


class CampaignTableModel(AbstractTableModel):
    """
    The table model for the campaings, with the
    getters and the setters.
    """

    def __init__(self, db):
        """
        The constructor of the model
        Args:
            db (object): The reference to the database instance.
        Returns:
            None
        """
        self._db = db

    def getRowCount(self):
        """
        Returns the total number of table records that are not deleted.
        Args:
            None
        Returns:
            int: The total number of table records that are not deleted.
        """
        try:
            return len(self._db.getActiveCampaignIndexes())
        except:
            print 'error in campaign table model'
            return 0

    def getColumnCount(self):
        """
        Returns the total number of table columns.
        Args:
            None
        Returns:
            int: The total number of table columns.
        """
        return 4

    def getColumnName(self, columnIndex):
        """
        Returns the name of a selected column
        Args:
            columnIndex (int): The index of the column.
        Returns:
            str: The name of the column.
        """
        if columnIndex == 0:
            return "Campaigns"
        elif columnIndex == 1:
            return "Queries A"
        elif columnIndex == 2:
            return "Queries B"
        elif columnIndex == 3:
            return "Results"
        return ""

    def getValueAt(self, rowIndex, columnIndex):
        """
        Returns the value of a selected row and a selected column
        Args:
            rowIndex (int): The index of the row.
            columnIndex (int): The index of the column.
        Returns:
            str: The value of the record
        """
        CampaignEntry = self._db.getCampaignByRow(rowIndex)
        if CampaignEntry:
            if columnIndex == 0:
                return str(CampaignEntry._name)
            elif columnIndex == 1:
                return CampaignEntry._Membership
            elif columnIndex == 2:
                return CampaignEntry._MembershipB
            elif columnIndex == 3:
                return CampaignEntry._Result
        return ""

    def addRow(self, row):
        """
        Notifies all listeners that the row was inserted.
        Args:
            row (int): The index of the inserted row
        Returns:
            None
        """
        self.fireTableRowsInserted(row, row)

    def setValueAt(self, val, row, col):
        """
        Sets the selected value in a selected row and a selected column record
        and notifies the listeners for the change.
        Args:
            val (depends on the class type of the record): The selected value
            row (int): The index of the row.
            col (int): The index of the column.
        Returns:
            None
        """
        CampaignEntry = self._db.getCampaignByRow(row)
        if CampaignEntry:
            if col == 0:
                CampaignEntry._name = val
            elif col == 1:
                CampaignEntry._Membership = val
            elif col == 2:
                CampaignEntry._MembershipB = val
            elif col == 3:
                CampaignEntry._Result = val

        self.fireTableCellUpdated(row, col)

    def isCellEditable(self, row, col):
        """
        Checks whether the value can be edited.
        Args:
            row (int): The index of the selected row
            col (int): The index of the selected column
        Returns:
            bool: A boolean value indicating whether the value is editable
        """
        return False

    def getColumnClass(self, columnIndex):
        """
        Returns the class type of the record of a selected column.
        Args:
            columnIndex (int): The index of the selected column
        Returns:
            str: The class type of the column's records
        """
        if columnIndex == 1:
            return int
        if columnIndex == 2:
            return int
        return str


class CampaignTable(JTable):
    """
    The table for the campaigns, with functions
    for its constructor and redrawing.
    """

    def __init__(self, extender, model):
        """
        The constructor of the table initiates the
        extender and model class variables.
        Args:
            extender (burp extension): A self reference to the extension
            model (abstract table class): The CampaignTableModel class
        """
        self._extender = extender
        self.setModel(model)
        return

    def redrawTable(self):
        """
        This function configures the columns width.
        """
        try:
            self.getModel().fireTableStructureChanged()
            self.getModel().fireTableDataChanged()
            self.getColumnModel().getColumn(0).setMinWidth(220)
            self.getColumnModel().getColumn(0).setMaxWidth(220)
            self.getColumnModel().getColumn(1).setMinWidth(125)
            self.getColumnModel().getColumn(1).setMaxWidth(125)
            self.getColumnModel().getColumn(2).setMinWidth(125)
            self.getColumnModel().getColumn(2).setMaxWidth(125)
            self.getColumnModel().getColumn(3).setMinWidth(150)
            self.getColumnModel().getColumn(3).setMaxWidth(150)
            self.getTableHeader().getDefaultRenderer().setHorizontalAlignment(JLabel.CENTER)
        except:
            pass


class LibraryTableModel(AbstractTableModel):
    """
    The table model for the library, with the
    getters and the setters.
    """

    def __init__(self, db, domain, category=None):
        """
        The constructor of the model
        Args:
            db (object): The reference to the database instance.
            domain (str): The category of the related data.
            category (str) The subcategory of the related data
        Returns:
            None
        """
        self._db = db
        self._domain = domain
        self._category = category

    def getRowCount(self):
        """
        Returns the total number of table records that are not deleted.
        Args:
            None
        Returns:
            int: The total number of table records that are not deleted.
        """
        try:
            return len(self._db.getActiveSettingIndexes(self._domain))
        except:
            print 'error in LibraryTableModel'
            return 0

    def getColumnCount(self):
        """
        Returns the total number of table columns.
        Args:
            None
        Returns:
            int: The total number of table columns.
        """
        return 3

    def getColumnName(self, columnIndex):
        """
        Returns the name of a selected column
        Args:
            columnIndex (int): The index of the column.
        Returns:
            str: The name of the column.
        """
        if columnIndex == 0:
            return "Name"
        elif columnIndex == 1:
            return "description"
        elif columnIndex == 2:
            return "Value"
        else:
            return ""
        return ""

    def getValueAt(self, rowIndex, columnIndex):
        """
        Returns the value of a selected row and a selected column
        Args:
            rowIndex (int): The index of the row.
            columnIndex (int): The index of the column.
        Returns:
            str: The value of the record
        """
        messageEntry = self._db.getSettingByRow(rowIndex, self._domain)
        if messageEntry:
            if columnIndex == 0:
                return messageEntry._name
            elif columnIndex == 1:
                return messageEntry._description
            elif columnIndex == 2:
                if self._category == 1:
                    return messageEntry._val1
                elif self._category == 2:
                    return messageEntry._val2
                elif self._category == 3:
                    return messageEntry._val3
                elif self._category == 4:
                    return messageEntry._val4
                elif self._category == 5:
                    return messageEntry._val5
                elif self._category == 6:
                    return messageEntry._val6
                elif self._category == 7:
                    return messageEntry._val7
                elif self._category == 8:
                    return messageEntry._val8
                else:
                    return messageEntry._value
            else:
                return ""
        return ""

    def addRow(self, row):
        """
        Notifies all listeners that the row was inserted.
        Args:
            row (int): The index of the inserted row
        Returns:
            None
        """
        self.fireTableRowsInserted(row, row)

    def setValueAt(self, val, row, col):
        """
        Sets the selected value in a selected row and a selected column record
        and notifies the listeners for the change.
        Args:
            val (depends on the class type of the record): The selected value
            row (int): The index of the row.
            col (int): The index of the column.
        Returns:
            None
        """
        messageEntry = self._db.getSettingByRow(row, self._domain)
        if col == 0:
            messageEntry._name = val
        elif col == 1:
            messageEntry._description = val
        elif col == 2:
            if self._category == 1:
                messageEntry._val1 = val
            elif self._category == 2:
                messageEntry._val2 = val
            elif self._category == 3:
                messageEntry._val3 = val
            elif self._category == 4:
                messageEntry._val4 = val
            elif self._category == 5:
                messageEntry._val5 = val
            elif self._category == 6:
                messageEntry._val6 = val
            elif self._category == 7:
                messageEntry._val7 = val
            elif self._category == 8:
                messageEntry._val8 = val
            else:
                messageEntry._value = val

        self.fireTableCellUpdated(row, col)

    def isCellEditable(self, row, col):
        """
        Checks whether the value can be edited.
        Args:
            row (int): The index of the selected row
            col (int): The index of the selected column
        Returns:
            bool: A boolean value indicating whether the value is editable
        """
        if col == 2:
            return True
        return False

    def getColumnClass(self, columnIndex):
        """
        Returns the class type of the record of a selected column.
        Args:
            columnIndex (int): The index of the selected column
        Returns:
            str: The class type of the column's records
        """
        if columnIndex == 2:
            return Boolean
        return str


class LibraryTable(JTable):
    """
    The table for the library, with functions
    for its constructor and redrawing.
    """

    def __init__(self, extender, model):
        """
        The constructor of the table
        Args:
            extender (burp extension): A self reference to the extension
            model (abstract table class): The LibraryTableModel class
        Returns:
            None
        """
        self._extender = extender
        self.setModel(model)
        return

    def redrawTable(self):
        """
        This function configures the columns width.
        """
        self.getModel().fireTableStructureChanged()
        self.getModel().fireTableDataChanged()
        self.getColumnModel().getColumn(0).setMinWidth(300)
        self.getColumnModel().getColumn(0).setMaxWidth(300)
        self.getColumnModel().getColumn(1).setMinWidth(400)
        self.getColumnModel().getColumn(1).setMaxWidth(400)
        self.getColumnModel().getColumn(2).setMinWidth(100)
        self.getColumnModel().getColumn(2).setMaxWidth(100)
        self.getTableHeader().getDefaultRenderer().setHorizontalAlignment(JLabel.CENTER)


class SettingsTableModel(AbstractTableModel):
    """
    The table model for the settings, with the
    getters and the setters.
    """

    def __init__(self, db, domain):
        """
        The constructor of the table
        Args:
            db (object): The reference to the database instance.
            domain (str): The category of the related data.
        Returns:
            None
        """
        self._db = db
        self._domain = domain

    def getRowCount(self):
        """
        Returns the total number of table records that are not deleted.
        Args:
            None
        Returns:
            int: The total number of table records that are not deleted.
        """
        try:
            return len(self._db.getActiveSettingIndexes(self._domain))
        except:
            return 0

    def getColumnCount(self):
        """
        Returns the total number of table columns.
        Args:
            None
        Returns:
            int: The total number of table columns.
        """
        return 2

    def getColumnName(self, columnIndex):
        """
        Returns the name of a selected column
        Args:
            columnIndex (int): The index of the column.
        Returns:
            str: The name of the column.
        """
        if columnIndex == 0:
            return "Name"
        elif columnIndex == 1:
            return "Value"
        else:
            return ""
        return ""

    def getValueAt(self, rowIndex, columnIndex):
        """
        Returns the value of a selected row and a selected column
        Args:
            rowIndex (int): The index of the row.
            columnIndex (int): The index of the column.
        Returns:
            str: The value of the record
        """
        messageEntry = self._db.getSettingByRow(rowIndex, self._domain)
        if messageEntry:
            if columnIndex == 0:
                return messageEntry._name
            elif columnIndex == 1:
                return messageEntry._value
            else:
                return ""
        return ""

    def addRow(self, row):
        """
        Notifies all listeners that the row was inserted.
        Args:
            row (int): The index of the inserted row
        Returns:
            None
        """
        self.fireTableRowsInserted(row, row)

    def setValueAt(self, val, row, col):
        """
        Sets the selected value in a selected row and a selected column record
        and notifies the listeners for the change.
        Args:
            val (depends on the class type of the record): The selected value
            row (int): The index of the row.
            col (int): The index of the column.
        Returns:
            None
        """
        messageEntry = self._db.getSettingByRow(row, self._domain)
        if col == 0:
            messageEntry._name = val
        elif col == 1:
            messageEntry._value = val

        self.fireTableCellUpdated(row, col)

    def isCellEditable(self, row, col):
        """
        Checks whether the value can be edited.
        Args:
            row (int): The index of the selected row
            col (int): The index of the selected column
        Returns:
            bool: A boolean value indicating whether the value is editable
        """
        if col == 1:
            return True
        return False

    def getColumnClass(self, columnIndex):
        """
        Returns the class type of the record of a selected column.
        Args:
            columnIndex (int): The index of the selected column
        Returns:
            str: The class type of the column's records
        """
        return str


class SettingsTable(JTable):
    """
    The table for the settings, with functions
    for its constructor and redrawing.
    """

    def __init__(self, extender, model):
        """
        The constructor of the table
        Args:
            extender (burp extension): A self reference to the extension
            model (abstract table class): The SettingsTableModel class
        Returns:
            None
        """
        self._extender = extender
        self.setModel(model)
        return

    def redrawTable(self):
        """
        This function configures the columns width.
        """
        self.getModel().fireTableStructureChanged()
        self.getModel().fireTableDataChanged()
        self.getColumnModel().getColumn(0).setMinWidth(200)
        self.getColumnModel().getColumn(0).setMaxWidth(200)
        self.getColumnModel().getColumn(1).setMinWidth(200)
        self.getColumnModel().getColumn(1).setMaxWidth(200)
        self.getTableHeader().getDefaultRenderer().setHorizontalAlignment(JLabel.CENTER)


class MessageTableModel(AbstractTableModel):
    """
    The table model for the messages, with the
    getters and the setters.
    """

    def __init__(self, db):
        """
        The constructor of the table
        Args:
            db (object): The reference to the database instance.
        Returns:
            None
        """
        self._db = db

    def getRowCount(self):
        """
        Returns the total number of table records that are not deleted.
        Args:
            None
        Returns:
            int: The total number of table records that are not deleted.
        """
        try:
            return len(self._db.getActiveMessageIndexes())
        except:
            return 0

    def getColumnCount(self):
        """
        Returns the total number of table columns.
        Args:
            None
        Returns:
            int: The total number of table columns.
        """
        return 7

    def getColumnName(self, columnIndex):
        """
        Returns the name of a selected column
        Args:
            columnIndex (int): The index of the column.
        Returns:
            str: The name of the column.
        """
        if columnIndex == 0:
            return "ID"
        elif columnIndex == 1:
            return "Host"
        elif columnIndex == 2:
            return "Method"
        elif columnIndex == 3:
            return "URL"
        elif columnIndex == 4:
            return "Success Regex"
        elif columnIndex == 5:
            return "Fail Regex"
        elif columnIndex == 6:
            return "Success Status"
        return ""

    def getValueAt(self, rowIndex, columnIndex):
        """
        Returns the value of a selected row and a selected column
        Args:
            rowIndex (int): The index of the row.
            columnIndex (int): The index of the column.
        Returns:
            str: The value of the record
        """
        messageEntry = self._db.getMessageByRow(rowIndex)
        if messageEntry:
            if columnIndex == 0:
                return str(messageEntry.getTableRow())
            elif columnIndex == 1:
                return messageEntry._host
            elif columnIndex == 2:
                return messageEntry._method
            elif columnIndex == 3:
                return messageEntry._name
            elif columnIndex == 4:
                return messageEntry._successRegex
            elif columnIndex == 5:
                return messageEntry._failRegex
            elif columnIndex == 6:
                return messageEntry._successStatus
        return ""

    def addRow(self, row):
        """
        Notifies all listeners that the row was inserted.
        Args:
            row (int): The index of the inserted row
        Returns:
            None
        """
        self.fireTableRowsInserted(row, row)

    def setValueAt(self, val, row, col):
        """
        Sets the selected value in a selected row and a selected column record
        and notifies the listeners for the change.
        Args:
            val (depends on the class type of the record): The selected value
            row (int): The index of the row.
            col (int): The index of the column.
        Returns:
            None
        """
        messageEntry = self._db.getMessageByRow(row)
        if col == 1:
            messageEntry._host = val
        elif col == 2:
            messageEntry._method = val
        elif col == 3:
            messageEntry._name = val
        elif col == 4:
            messageEntry._successRegex = val
        elif col == 5:
            messageEntry._failRegex = val
        elif col == 6:
            messageEntry._successStatus = val
        else:
            roleIndex = self._db.getRoleByMColumn(col)._index
            messageEntry.addRoleByIndex(roleIndex, val)
        self.fireTableCellUpdated(row, col)

    def isCellEditable(self, row, col):
        """
        Checks whether the value can be edited.
        Args:
            row (int): The index of the selected row
            col (int): The index of the selected column
        Returns:
            bool: A boolean value indicating whether the value is editable
        """
        if col == 5:
            return True
        if col == 4:
            return True
        return False

    def getColumnClass(self, columnIndex):
        """
        Returns the class type of the record of a selected column.
        Args:
            columnIndex (int): The index of the selected column
        Returns:
            str: The class type of the column's records
        """
        if columnIndex < 6:
            return str
        else:
            return Boolean


class MessageTable(JTable):
    """
    The table for the messages, with functions
    for its constructor and redrawing.
    """

    def __init__(self, extender, model):
        """
        The constructor of the table
        Args:
            extender (burp extension): A self reference to the extension
            model (abstract table class): The MessagesTableModel class
        Returns:
            None
        """
        self._extender = extender
        self.setModel(model)
        return

    def changeSelection(self, row, col, toggle, extend):

        # show the message entry for the selected row
        selectedMessage = self.getModel()._db.getMessageByRow(row)
        self._extender._tabs.removeAll()

        # NOTE: testing if .locked is ok here since its a manual operation
        if self.getModel()._db.lock.locked():
            # Provide some feedback on a click
            self.redrawTable()
            return

        # Create original Request tab and set default tab to Request
        # Then Create test tabs and set the default tab to Response for easy
        # analysis
        originalTab = self.createRequestTabs(selectedMessage._requestResponse)
        originalTab.setSelectedIndex(0)
        self._extender._tabs.addTab("Original", originalTab)
        for campaignIndex in selectedMessage._campaignRuns.keys():
            if not self.getModel()._db.arrayOfCampaigns[
                    campaignIndex].isDeleted():
                tabname = str(
                    self.getModel()._db.arrayOfCampaigns[campaignIndex]._name)
                self._extender._tabs.addTab(
                    tabname, self.createRequestTabs(
                        selectedMessage._campaignRuns[campaignIndex]))

        self._extender._currentlyDisplayedItem = selectedMessage._requestResponse
        JTable.changeSelection(self, row, col, toggle, extend)
        return

    def createRequestTabs(self, requestResponse):
        requestTabs = JTabbedPane()
        requestViewer = self._extender._callbacks.createMessageEditor(
            self._extender, False)
        responseViewer = self._extender._callbacks.createMessageEditor(
            self._extender, False)
        requestTabs.addTab("Request", requestViewer.getComponent())
        requestTabs.addTab("Response", responseViewer.getComponent())
        self._extender._callbacks.customizeUiComponent(requestTabs)
        requestViewer.setMessage(requestResponse.getRequest(), True)
        if requestResponse.getResponse():
            responseViewer.setMessage(requestResponse.getResponse(), False)
            requestTabs.setSelectedIndex(1)

        return requestTabs

    def redrawTable(self):
        """
        This function configures the columns width.
        """
        self.getModel().fireTableStructureChanged()
        self.getModel().fireTableDataChanged()
        self.getColumnModel().getColumn(0).setMinWidth(30)
        self.getColumnModel().getColumn(0).setMaxWidth(30)
        self.getColumnModel().getColumn(1).setMinWidth(150)
        self.getColumnModel().getColumn(1).setMaxWidth(150)
        self.getColumnModel().getColumn(2).setMinWidth(60)
        self.getColumnModel().getColumn(2).setMaxWidth(60)
        self.getColumnModel().getColumn(3).setMinWidth(150)
        self.getColumnModel().getColumn(3).setMaxWidth(150)
        self.getColumnModel().getColumn(4).setMinWidth(150)
        self.getColumnModel().getColumn(4).setMaxWidth(150)
        self.getColumnModel().getColumn(5).setMinWidth(150)
        self.getColumnModel().getColumn(5).setMaxWidth(150)
        self.getColumnModel().getColumn(6).setMinWidth(100)
        self.getColumnModel().getColumn(6).setMaxWidth(100)


class SuccessBooleanRenderer(JCheckBox, TableCellRenderer):

    def __init__(self, db):
        """
        The constructor of the renderer
        Args:
            db (object): The reference to the database instance.
        Returns:
            None
        """
        self.setOpaque(True)
        self.setHorizontalAlignment(JLabel.CENTER)
        self._db = db

    def getTableCellRendererComponent(
            self,
            table,
            value,
            isSelected,
            hasFocus,
            row,
            column):
        if value:
            self.setSelected(True)
        else:
            self.setSelected(False)
        if isSelected:
            self.setForeground(table.getSelectionForeground())
            self.setBackground(table.getSelectionBackground())
        else:
            self.setForeground(table.getForeground())
            self.setBackground(table.getBackground())

        return self


class MessageEntry:
    """
    The schema for the row of messages table
    """

    def __init__(
            self,
            index,
            tableRow,
            requestResponse,
            host="",
            method="",
            name="",
            selectedparameter="",
            regex="^HTTP/1.1 200 OK",
            failRegex="(^HTTP/1.1 403|block|impact)",
            deleted=False,
            status=True):
        """
        The constructor for the MessageEntry record.
        Args:
            index (int): The index of the messages array for this record
            tableRow (int): The index of the messages tables for this record
            requestResponse (str): The saved buffer of the burp request-response
            host (str): The targetted host
            method (str): The used HTTP method
            name (str): The HTTP URL path
            selectedparameter (str): The parameter of the HTTP request
            regex (str): A regex that if matches the response indicates a success
            failRegex (str): A regex that if matches the response indicates a failure
            deleted (bool): A boolean value indicating whether the record is deleted.
            status (bool): A boolean value indicating whether the record is selected.
        Returns:
            None
        """
        self._index = index
        self._tableRow = tableRow
        self._requestResponse = requestResponse
        self._host = host
        self._method = method
        self._name = name
        self._selectedparameter = selectedparameter
        self._successRegex = regex
        self._failRegex = failRegex
        self._successStatus = status
        self._deleted = deleted
        self._campaignRuns = {}
        self._roleResults = {}
        return

    def isDeleted(self):
        """
        Returns a boolean value indicating if record is deleted.
        Args:
            None
        Returns:
            Bool: Valude indicating if record is deleted.
        """
        return self._deleted

    def updateTableRow(self, row):
        """
        Changes the content of the row with the input
        Args:
            row (int): A new table index
        Returns:
            None
        """
        self._tableRow = row

    def getTableRow(self):
        """
        Returns the current table index of the record
        Args:
            None
        Returns:
            int: Table index
        """
        return self._tableRow


class SettingEntry:
    """
    The schema for the row of settings table
    """

    def __init__(
            self,
            index,
            rowIndex,
            name,
            value="",
            domain=None,
            description=None,
            path=None):
        """
        The constructor for the MessageEntry record.
        Args:
            index (int): The index of the messages array for this record
            rowIndex (int): The index of the messages tables for this record
            requestResponse (str): The saved buffer of the burp request-response
            name (str): The HTTP URL path

        Returns:
            None
        """
        self._index = index
        self._name = name
        self._deleted = False
        self._tableRow = rowIndex
        self._value = value
        self._val1 = value
        self._val2 = value
        self._val3 = value
        self._val4 = value
        self._val5 = value
        self._val6 = value
        self._val7 = value
        self._val8 = value
        self._path = path
        self._domain = domain
        self._description = description
        return

    def isDeleted(self):
        """
        Returns a boolean value indicating if record is deleted.
        Args:
            None
        Returns:
            Bool: Valude indicating if record is deleted.
        """
        return self._deleted

    def updateTableRow(self, row):
        """
        Changes the content of the row with the input
        Args:
            row (int): A new table index
        Returns:
            None
        """
        self._tableRow = row

    def getTableRow(self):
        """
        Returns the current table index of the record
        Args:
            None
        Returns:
            int: Table index
        """
        return self._tableRow


class CampaignEntry:
    """
    The schema for the row of campaigns table
    """

    def __init__(
            self,
            index,
            rowIndex,
            name,
            Membership="0",
            MembershipB="0",
            Result="Running",
            Stats="Campaing is still running..."):
        self._index = index
        self._name = name
        self._Membership = Membership
        self._MembershipB = MembershipB
        self._Result = Result
        self._Stats = Stats
        self._deleted = False
        self._tableRow = rowIndex
        self.thread = None
        self._inputlist = None

        return

    def isDeleted(self):
        """
        Returns a boolean value indicating if record is deleted.
        Args:
            None
        Returns:
            Bool: Valude
        """
        return self._deleted

    def updateTableRow(self, row):
        """
        Changes the content of the row with the input
        Args:
            row (int): A new table index
        Returns:
            None
        """
        self._tableRow = row

    def getTableRow(self):
        """
        Returns the current table index of the record
        Args:
            None
        Returns:
            int: Table index
        """
        return self._tableRow
