
#from sortmanager import SortManager
import inspect
import uuid
from collections import namedtuple


class Task():
    def __init__(self, id, pos, classname, beforeCallBack, CallBack, args):
        self.id = id
        self.className = classname
        self.beforeCallBack = beforeCallBack
        self.CallBack = CallBack
        self.args = args
        self.moveto = self.__createNamedTuple(pos)
        
    def __createNamedTuple(self, tuple):
        Position = namedtuple('Position', ['x', 'y', 'z'])
        if len(tuple) > 2:
            z = float(tuple[2])
        else:
            z = 0.0
        return Position(x=float(tuple[0]), y=float(tuple[1]), z=z)

    def run(self, robot):
        if self.beforeCallBack is not None: 
            self.beforeCallBack(*self.args)
            
        # print(self.__curentTask.id, "doing")
        # print(self.__curentTask.moveto.x, self.__curentTask.moveto.y, self.__curentTask.moveto.z) 
        #TODO: add loging system as i like :)                

        robot._navigate_to_anchor(self.moveto.x, self.moveto.y, self.moveto.z)
        
        self.CallBack(robot, *self.args)
            
        # print(self.__curentTask.id, "done")

        
class TaskManager():
    def __init__(self, robot, config):
        self.__tasks = []
        self.__curentTask = None
        self.robot = robot
        self.config = config
        #self.sortmanager = SortManager()  TODO: @LosVocelos, I guess, it won't be difficult.

    def getTasks(self):
        return self.__tasks
         
    def createNewTask(self, priority, pos, CallBack, beforeCallBack=None, *args):
        classname = inspect.stack()[1][0].f_locals['self'].__class__.__name__ # get classname from executor class
        task = Task(uuid.uuid4(), pos, classname, beforeCallBack, CallBack, args)
        self.__tasks.insert(0, task)
        return task
 
    def delTask(task):
        pass

    def getCurentTask(self):
        return self.__curentTask
        
    def TaskLoop(self):
        while 1:
            while len(self.__tasks) > 0:
                self.__curentTask = self.__tasks.pop(0)
                self.__curentTask.run(self.robot)
            if self.robot.powerState:
                    self.robot.powerControl(False)
            if self.robot.powerState:
                self.robot.powerControl(False)
                
                
            
             
