import sys, os, imp
try:
    imp.find_module('pywrapfst')
    mymodule_path = "/usr/local/lib"
    try:
        sys.path.append(mymodule_path)
        import pywrapfst
    except ImportError:
       if sys.platform == 'win32':
           os.environ['PATH'] = mymodule_path
       elif sys.platform == 'darwin':
           os.environ['DYLD_LIBRARY_PATH'] = mymodule_path
       else:
           os.environ['LD_LIBRARY_PATH'] = mymodule_path
       args = [sys.executable]
       args.extend(sys.argv)
       os.execv(sys.executable, args)
except:
    pass

from cliff.app import App
from cliff.commandmanager import CommandManager
from cliff.complete import CompleteCommand
STATE = 0
class LightBulb(App):

    def __init__(self):
        super(LightBulb, self).__init__(
            description='LightBulb App',
            version='0.1',
            command_manager=CommandManager('cliff.lightbulb'),
            deferred_help=False,
            )

    def initialize_app(self, argv):
        print """"""
        print """"""
        print """ __        __            __          __      _______             __  __"""
        print """/  |      /  |          /  |        /  |    /       \           /  |/  |"""
        print """$$ |      $$/   ______  $$ |____   _$$ |_   $$$$$$$  | __    __ $$ |$$ |___"""
        print """$$ |      /  | /      \ $$      \ / $$   |  $$ |__$$ |/  |  /  |$$ |$$      \\"""
        print """$$ |      $$ |/$$$$$$  |$$$$$$$  |$$$$$$/   $$    $$< $$ |  $$ |$$ |$$$$$$$  |"""
        print """$$ |      $$ |$$ |  $$ |$$ |  $$ |  $$ | __ $$$$$$$  |$$ |  $$ |$$ |$$ |  $$ |"""
        print """$$ |_____ $$ |$$ \\__$$ |$$ |  $$ |  $$ |/  |$$ |__$$ |$$ \\__$$ |$$ |$$ |__$$ |"""
        print """$$       |$$ |$$    $$ |$$ |  $$ |  $$  $$/ $$    $$/ $$    $$/ $$ |$$    $$/"""
        print """$$$$$$$$/ $$/  $$$$$$$ |$$/   $$/    $$$$/  $$$$$$$/   $$$$$$/  $$/ $$$$$$$/"""
        print """              /  \__$$ |"""
        print """              $$    $$/"""
        print """               $$$$$$/"""
        print """"""
        print """                            George Argyros, Ioannis Stais          """
        print """"""
        self.LOG.debug('initialize_app')

    def prepare_to_run_command(self, cmd):
        global STATE
        self.LOG.debug('prepare_to_run_command %s', cmd.__class__.__name__)
        if cmd.__class__.__name__ == "Use":
            if STATE == 0:
                STATE = 1
            for key in self.command_manager.commands.keys():
                del(self.command_manager.commands[key])
            self.command_manager.load_commands('cliff.modulehandler')
            self.command_manager.add_command('complete', CompleteCommand)


        if cmd.__class__.__name__ == "Library":
            if STATE == 0:
                STATE = 1
            elif STATE == 1:
                STATE = 2
            for key in self.command_manager.commands.keys():
                del(self.command_manager.commands[key])
            self.command_manager.load_commands('cliff.libraryhandler')
            self.command_manager.add_command('complete', CompleteCommand)


        if cmd.__class__.__name__ == "Back" or cmd.__class__.__name__ == "LibraryBack":
            if STATE == 1:
                STATE = 0
                for key in self.command_manager.commands.keys():
                    del(self.command_manager.commands[key])
                self.command_manager.load_commands('cliff.lightbulb')
                self.command_manager.add_command('complete', CompleteCommand)
            elif STATE == 2:
                STATE = 1
                for key in self.command_manager.commands.keys():
                    del (self.command_manager.commands[key])
                self.command_manager.load_commands('cliff.modulehandler')
                self.command_manager.add_command('complete', CompleteCommand)



    def clean_up(self, cmd, result, err):
        global STATE
        if cmd.__class__.__name__ == "Use" and result == False:
            if STATE == 1:
                STATE = 0
            for key in self.command_manager.commands.keys():
                del(self.command_manager.commands[key])
            self.command_manager.load_commands('cliff.lightbulb')
            self.command_manager.add_command('complete', CompleteCommand)

        self.LOG.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.LOG.debug('got an error: %s', err)


def main(argv=sys.argv[1:]):
    myapp = LightBulb()
    return myapp.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))