from Plugins import Base
from taskmanager import TaskManager
from config import Config
from robot import Robot
from time import sleep
import bosdyn.client.lease


if __name__ == '__main__':
    config = Config()
    robot = Robot(config)
    taskmanager = TaskManager(robot, config)
    with bosdyn.client.lease.LeaseKeepAlive(robot.lease_client, must_acquire=True, return_at_exit=True):
        
        for Plugin in Base.plugins:
           plugin = Plugin(taskmanager)
        taskmanager.TaskLoop()
