import Plugins
class ExamplePlugin(Plugins.Base):
    def __init__(self, taskmanger):
        print("im example plugin!")
        taskmanger.addTask()
