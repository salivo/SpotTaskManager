from Plugins import Base
from taskmanager import TaskManager
from config import Config
from robot import Robot

if __name__ == '__main__':
    config = Config()
    robot = testRobot()
    taskmanager = TaskManager(robot, config)
    for Plugin in Base.plugins:
       plugin = Plugin(taskmanager)
    taskmanager.TaskLoop()
