"""
This file contains all the handlers that will be used by
the GOFA and SFADiff modules. The handlers can be new
implementations (e.g. BurpHTTPHandler) or just interfaces
to the lightbulb's handlers (that allow us to perform
small changes.
"""
from lightbulb.core.utils.rawhttphandler import RawHTTPHandler
from lightbulb.core.utils.browserhandler import BrowserHandler
from lightbulb.core.utils.browserfilterhandler import BrowserFilterHandler
from lightbulb.core.utils.sqlhandler import SQLHandler
import base64


class BurpBrowserHandler(BrowserHandler):
    """
    This is an interface to the lightbulb's BrowserHandler.
    The reason that we use this interface is because we want
    to override the "query" function and perform a check
    for the campaign's "deleted" variable. As a result,
    we can stop the execution when the user deletes the
    campaign. Also, it can be use to gather live statistics.
    """

    def __init__(self, configuration=None):
        """
        The function overrides lightbulb's Browser handler constructor
        and defines two new class variables, (ID), (PARENT) and (CAMPAIGN).
        Args:
            configuration (dict):  The dictionary to be used as a parameter during
            the initialization of the original handler class.
        Returns:
            None
        """
        self.id = None
        self.parent = None
        self.campaign = None
        self.membershiprequests = 0
        BrowserHandler.__init__(self, configuration)


    def setup(self, configuration):
        """
        The function overrides lightbulb's Browser handler function
        that does the setup for the handler. It configures two new
        class variables, (PARENT) and (CAMPAIGN), and then calls the
        original lightbulb's handler setup function.
        Args:
            configuration (dict):  The dictionary to be used as a parameter during
            the initialization of the original handler class. It also contains the
            new class variables that must be set (ID), (PARENT) and (CAMPAIGN)
        Returns:
            None
        """
        BrowserHandler.setup(self, configuration)
        self.parent = configuration['PARENT']
        self.campaign = configuration['CAMPAIGN']
        self.id = configuration['ID']

    def query(self, string):
        """
        The function overrides lightbulb's Browser handler function
        that performs the query. It checks for the "deleted" variable
        and if it is set as True, it terminates the thread. Otherwise,
        it calls the original lightbulb's handler query function
        and returns the result. The check is made using the
        (PARENT) and (CAMPAIGN) class variables.
        Args:
            input_string (str): Input for the target Mealy machine
        Returns:
            bool: the output of the target Mealy Machine on input input_string.
        """
        if self.campaign is not None and self.parent._db.arrayOfCampaigns[
                self.campaign]._deleted:
            BrowserHandler.__del__(self)
            exit()
        self.membershiprequests = self.membershiprequests  + 1
        found = BrowserHandler.query(self, string)
        self.parent.handleUpdateCampaign(self.campaign, self.id, self.membershiprequests)
        return found


class BurpBrowserFilterHandler(BrowserFilterHandler):
    """
    This is an interface to the lightbulb's BrowserFilterHandler.
    The reason that we use this interface is because we want
    to override the "query" function and perform a check
    for the campaign's "deleted" variable. As a result,
    we can stop the execution when the user deletes the
    campaign. Also, it can be use to gather live statistics.
    """

    def __init__(self, configuration=None):
        """
        The function overrides lightbulb's BrowserFilter handler constructor
        and defines two new class variables, (ID), (PARENT) and (CAMPAIGN).
        Args:
            configuration (dict):  The dictionary to be used as a parameter during
            the initialization of the original handler class.
        Returns:
            None
        """
        self.parent = None
        self.campaign = None
        self.id = None
        self.membershiprequests = 0
        BrowserFilterHandler.__init__(self, configuration)


    def setup(self, configuration):
        """
        The function overrides lightbulb's BrowserFilter handler function
        that does the setup for the handler. It configures two new
        class variables, (PARENT) and (CAMPAIGN), and then calls the
        original lightbulb's handler setup function.
        Args:
            configuration (dict):  The dictionary to be used as a parameter during
            the initialization of the original handler class. It also contains the
            new class variables that must be set (ID), (PARENT) and (CAMPAIGN)
        Returns:
            None
        """
        BrowserFilterHandler.setup(self, configuration)
        self.parent = configuration['PARENT']
        self.campaign = configuration['CAMPAIGN']
        self.id = configuration['ID']

    def query(self, string):
        """
        The function overrides lightbulb's BrowserFitler handler function
        that performs the query. It checks for the "deleted" variable
        and if it is set as True, it terminates the thread. Otherwise,
        it calls the original lightbulb's handler query function
        and returns the result. The check is made using the
        (PARENT) and (CAMPAIGN) class variables.
        Args:
            input_string (str): Input for the target Mealy machine
        Returns:
            bool: the output of the target Mealy Machine on input input_string.
        """
        if self.campaign is not None and self.parent._db.arrayOfCampaigns[
                self.campaign]._deleted:
            BrowserFilterHandler.__del__(self)
            exit()
        self.membershiprequests = self.membershiprequests  + 1
        found = BrowserFilterHandler.query(self, string)
        self.parent.handleUpdateCampaign(self.campaign, self.id, self.membershiprequests)
        return found


class BurpSQLHandler(SQLHandler):
    """
    This is an interface to the lightbulb's BurpSQLHandler.
    The reason that we use this interface is because we want
    to override the "query" function and perform a check
    for the campaign's "deleted" variable. As a result,
    we can stop the execution when the user deletes the
    campaign. Also, it can be use to gather live statistics.
    """

    def __init__(self, configuration=None):
        """
        The function overrides lightbulb's SQL handler constructor
        and defines two new class variables, (ID), (PARENT) and (CAMPAIGN).
        Args:
            configuration (dict):  The dictionary to be used as a parameter during
            the initialization of the original handler class.
        Returns:
            None
        """
        self.id = None
        self.parent = None
        self.campaign = None
        self.membershiprequests = 0
        SQLHandler.__init__(self, configuration)

    def setup(self, configuration):
        """
        The function overrides lightbulb's SQL handler function
        that does the setup for the handler. It configures two new
        class variables, (PARENT) and (CAMPAIGN), and then calls the
        original lightbulb's handler setup function.
        Args:
            configuration (dict):  The dictionary to be used as a parameter during
            the initialization of the original handler class. It also contains the
            new class variables that must be set (ID), (PARENT) and (CAMPAIGN)
        Returns:
            None
        """
        SQLHandler.setup(self, configuration)
        self.parent = configuration['PARENT']
        self.campaign = configuration['CAMPAIGN']
        self.id = configuration['ID']

    def query(self, string):
        """
        The function overrides lightbulb's SQLHandler handler function
        that performs the query. It checks for the "deleted" variable
        and if it is set as True, it terminates the thread. Otherwise,
        it calls the original lightbulb's handler query function
        and returns the result. The check is made using the
        (PARENT) and (CAMPAIGN) class variables.
        Args:
            input_string (str): Input for the target Mealy machine
        Returns:
            bool: the output of the target Mealy Machine on input input_string.
        """
        if self.campaign is not None and self.parent._db.arrayOfCampaigns[
                self.campaign]._deleted:
            SQLHandler.__del__(self)
            exit()
        self.membershiprequests = self.membershiprequests  + 1
        found = SQLHandler.query(self, string)
        self.parent.handleUpdateCampaign(self.campaign, self.id, self.membershiprequests)
        return found


class BurpHTTPHandler(RawHTTPHandler):
    """
    This is a new Handler implementation for the membership requests,
    that performs HTTP requests through Burp Proxy, and is going
    to the lightbulb's HTTP Handler. The reason that we use this
    implementation is because we want to have full integration with
    the Burp's recorded HTTP requests, and be able to present them
    to the user.
    """

    def __init__(self, configuration=None):
        """
        This is the constructor of BurpHTTPHandler. It defines a number
        of class variables, and calls the setup function with the
        input configuration variable.
        Args:
            configuration (dict):  The dictionary to be used as a parameter
            in the setup function.
        Returns:
            None
        """
        self.targetparameter = None
        self.parent = None
        self.targettype = None
        self.index = None
        self.membershiprequests = 0
        self.campaign = None
        self.id = 1
        RawHTTPHandler.__init__(self, configuration)

    def setup(self, configuration):
        """
        The function performs the BurpHTTPHandler setup. It initializes
        the class variables with user's selected values, and calls the
        MembershipRequestsInit function from Burp extension. This function
        will return configuration values obtained from the Burp proxy
        window.
        Args:
            configuration (dict):  The dictionary that contains user's
            selected values for the class variables.
        Returns:
            None
        """
        self.parent = configuration['PARENT']
        self.campaign = configuration['CAMPAIGN']
        self.show = configuration['SHOW']
        self.id = configuration['ID']
        self.index = configuration['INDEX']
        self.targetparameter = configuration['PARAM']
        self.message, self.host, self.method, self.path, \
        self.targettype, self.success_regex, self.fail_regex, \
        self.parameters, self.port, self.https \
            = self.parent.MembershipRequestsInit(self.index, self.targetparameter)
        configuration['MESSAGE'] = base64.b64encode(bytes(self.message))
        configuration['HOST'] = self.host
        configuration['PORT'] = self.port
        configuration['HTTPS'] = self.https
        configuration['BLOCK'] = self.fail_regex
        configuration['BYPASS'] = self.success_regex
        RawHTTPHandler.setup(self, configuration)

    def query(self, string):
        """
       The function implements the membership requests as an HTTP request.
       The actual request is made using the MembershipRequest located at the
       Burp Extension.
       Args:
            input_string (str): Input for the target Mealy machine
        Returns:
            bool: the output of the target Mealy Machine on input input_string.
       """
        if self.campaign is not None and self.parent._db.arrayOfCampaigns[
                self.campaign]._deleted:
            exit()
        self.membershiprequests = self.membershiprequests + 1
        found, request, response = RawHTTPHandler.query(self, string, self.show)


        if string:
            print 'Perform membership request at input ' + string + ' - ', found
        if self.show == "true":
            self.parent.updateMembershipRequest(
            self.index, self.host, self.method,
            self.path, self.targetparameter, string,
            self.success_regex, self.fail_regex,
            self.parameters, request, response, found)

        self.parent.handleUpdateCampaign(self.campaign, self.id, self.membershiprequests)

        return found



class NativeHandler():
    def __init__(self, campaign = None, parent = None):
        self.campaign = campaign
        self.parent = parent
        self.handler_a_memberships = 0
        self.handler_b_memberships = 0

    def readline(self, string):
        if self.campaign is not None and self.parent._db.arrayOfCampaigns[
            self.campaign]._deleted:
            exit()
        if "Handler_A_Membership" in string and "define" not in string:
            self.handler_a_memberships = self.handler_a_memberships + 1
            self.parent._db.updateCampaign(self.campaign, 1, self.handler_a_memberships)
            self.parent._CampaignTable.redrawTable()
        if "Handler_B_Membership" in string and "define" not in string:
            self.handler_b_memberships = self.handler_b_memberships + 1
            self.parent._db.updateCampaign(self.campaign, 2, self.handler_b_memberships)
            self.parent._CampaignTable.redrawTable()