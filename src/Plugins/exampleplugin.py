
import bosdyn.geometry
from bosdyn.client.robot_command import RobotCommandBuilder
import time

import Plugins

PRIORITY = 4

class ExamplePlugin(Plugins.Base):

    def __init__(self, taskmanger):
        print("i'm example plugin!")
        MoveSpotToPoint = taskmanger.Point(4,1)
        taskmanger.createNewTask(MoveSpotToPoint,PRIORITY,self.callbacker)
        MoveSpotToPoint = taskmanger.Point(3,0)
        taskmanger.createNewTask(MoveSpotToPoint,PRIORITY,self.callbacker)
            
    def callbacker(self, robot):
        footprint_R_body = bosdyn.geometry.EulerZXY(yaw=0.4, roll=0.4, pitch=0.4)
        cmd = RobotCommandBuilder.synchro_stand_command(footprint_R_body=footprint_R_body)
        robot.command_client.robot_command(cmd)
        print("hehe")
        time.sleep(2)
        
    
