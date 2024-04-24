
#from sortmanager import SortManager
import inspect
import uuid
from collections import namedtuple



class Task():
    def __init__(self, id, point, classname, beforeCallBack, CallBack, args):
        self.id = id
        self.className = classname
        self.beforeCallBack = beforeCallBack
        self.CallBack = CallBack
        self.args = args
        self.point = point

    def run(self, robot):
        if self.beforeCallBack is not None: 
            self.beforeCallBack(*self.args)
        # print(self.__curentTask.id, "doing")
        # print(self.__curentTask.moveto.x, self.__curentTask.moveto.y, self.__curentTask.moveto.z) 
        #TODO: add loging system as i like :)                
        robot._navigate_to_anchor(self.point)
        self.CallBack(robot, *self.args)
        # print(self.__curentTask.id, "done")
            
class TaskManager():
    def __init__(self, robot, config):
        self.__tasks = []
        self.__curentTask = None
        self.__robot = robot
        self.config = config
        #self.sortmanager = SortManager()  TODO: @LosVocelos, I guess, it won't be difficult.

    class Point():
        def __init__(self, x, y, z=0):
            self.x = float(x)
            self.y = float(y)
            self.z = float(z)
            
    def TaskLoop(self):
        try:    
            while 1:
                while len(self.__tasks) > 0:
                    self.__curentTask = self.__tasks.pop(0)
                    self.__curentTask.run(self.__robot)
                if self.__robot.powerState:
                        self.__robot.controlPower(False)
        except KeyboardInterrupt:
            return

    def createNewTask(self, point, priority, CallBack, beforeCallBack=None, *args):
        classname = inspect.stack()[1][0].f_locals['self'].__class__.__name__ # get classname from executor class
        task = Task(uuid.uuid4(), point, classname, beforeCallBack, CallBack, args)
        self.__tasks.append(task) #TODO: insert(pos) with sortmanager.getpos() 
        return task

    def getTasks(self):
        return self.__tasks
            
    def delTask(task):
        pass #TODO

    def getCurentTask(self):
        return self.__curentTask
        
    
                
                
            
             
