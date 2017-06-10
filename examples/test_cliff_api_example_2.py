from cliff.app import App
from cliff.commandmanager import CommandManager

from lightbulb.cli.use import StartSaved, Use, Define, Back

class parsed_args():
    module = None
    set = None

class LightBulb(App):
    def __init__(self):
        super(LightBulb, self).__init__(
            description='LightBulb App',
            version='0.1',
            command_manager=CommandManager('cliff.lightbulb'),
            deferred_help=False,
        )
        self.startsaved = StartSaved(self, self, None)
        self.use = Use(self, self, None)
        self.back = Back(self, self, None)
        self.define = Define(self, self, None)

    def startlearning(self):
        print 'use HTTPHandler as my_query_handler'
        target = parsed_args()
        target.module = ["HTTPHandler", "as", "my_query_handler"]
        self.use.take_action(target)

        print 'define URL http://83.212.105.5/PHPIDS07/'
        target = parsed_args()
        target.set = ["URL", "http://83.212.105.5/PHPIDS07/"]
        self.define.take_action(target)
        target = parsed_args()
        target.set = ["BLOCK", "impact"]
        self.define.take_action(target)
        target = parsed_args()
        target.set = ["PARAM", "lala"]
        self.define.take_action(target)
        print 'back'
        self.back.take_action(target)

        print 'use GOFA as my_gofa'
        target = parsed_args()
        target.module = ["gofa", "as", "mygofa"]
        self.use.take_action(target)
        print 'define TESTS_FILE {library}/regex/PHPIDS070/12.y'
        target = parsed_args()
        target.set = ["TESTS_FILE", "{library}/regex/PHPIDS070/12.y"]
        self.define.take_action(target)
        target = parsed_args()
        target.set = ["TESTS_FILE_TYPE", "FLEX"]
        self.define.take_action(target)
        print 'define HANDLER my_query_handler'
        target = parsed_args()
        target.set = ["HANDLER", "my_query_handler"]
        self.define.take_action(target)
        print 'back'
        self.back.take_action(target)

        print 'start my_gofa'
        target = parsed_args()
        details = self.startsaved.take_action(target)
        print details

myapp = LightBulb()
myapp.startlearning()