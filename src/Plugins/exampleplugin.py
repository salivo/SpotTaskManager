import Plugins
class ExamplePlugin(Plugins.Base):
    def callbacker(self):
        print("hello from callbacker!")
    def __init__(self, taskmanger):
        print("im example plugin!")
        taskmanger.addTask(1,(0,0),self.callbacker)
