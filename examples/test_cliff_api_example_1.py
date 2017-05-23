from cliff.app import App
from cliff.commandmanager import CommandManager
from lightbulb.cli.show import LibraryModules, LibraryCat

class parsed_args():
    folder = None
    component = None


class LightBulb(App):

    def __init__(self):
        super(LightBulb, self).__init__(
            description='LightBulb App',
            version='0.1',
            command_manager=CommandManager('cliff.lightbulb'),
            deferred_help=False,
            )
        self.library = LibraryModules(self,self,None)
        self.libraryCat = LibraryCat(self,self,None)

    def readlibrary(self, folder):
        try:
            target = parsed_args()
            target.folder = folder
            details = self.library.take_action(target)[1]
            if len(details) > 0:
                for x in details:
                    if x:
                        print x
                        if x[2] == 'Folder':
                            self.readlibrary(folder + "/" + x[0])
                        else:
                            if x[2] != 'FST':
                                print "Reading ", folder + "/" + x[0]
                                self.readlibraryfile(folder + "/" + x[0])
        except:
            pass

    def readlibraryfile(self, requestedfile):
        target = parsed_args()
        target.component = requestedfile
        details = self.libraryCat.take_action(target)[1]
        if len(details) > 0:
            print details


def readlibrary(self, folder):
    try:
        target = parsed_args()
        target.folder = folder
        details = self.library.take_action(target)[1]
        if len(details) > 0:
            for x in details:
                if x:
                    print x
                    if x[2] == 'Folder':
                        self.readlibrary(folder + "/" + x[0])
                    else:
                        if x[2] != 'FST':
                            print "Reading ", folder + "/" + x[0]
                            self.readlibraryfile(folder + "/" + x[0])
    except:
        pass


def readlibraryfile(self, requestedfile):
    target = parsed_args()
    target.component = requestedfile
    details = self.libraryCat.take_action(target)[1]
    if len(details) > 0:
        print details

myapp = LightBulb()
myapp.readlibrary(".")