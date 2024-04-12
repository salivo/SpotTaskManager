from Plugins import Base
from taskmanager import TaskManager
if __name__ == '__main__':
    taskmanager = TaskManager()
    for Plugin in Base.plugins:
        plugin = Plugin(taskmanager)
