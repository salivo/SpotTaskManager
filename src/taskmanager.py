#from sortmanager import SortManager
import inspect
import uuid

class MoveTo():
    def __init__(self, x, y, z=0.0):
        self.x = x
        self.y = y
        self.z = z

class Task():
    def __init__(self, id, moveto, classname, beforeCallBack, CallBack, args):
        self.id = id
        self.className = classname
        self.beforeCallBack = beforeCallBack
        self.CallBack = CallBack
        self.args = args
        self.moveto = moveto
        
class TaskManager():
    def __init__(self, robot, config):
        self.__tasks = []
        self.__curentTask = None
        self.robot = robot
        self.config = config
        #self.sortmanager = SortManager()

    def getTasks(self):
        return self.__tasks
         
    def addTask(self, priority, pos, CallBack, beforeCallBack=None, *args):
    
        moveto = MoveTo(pos[0],pos[1])
        if len(pos) > 2:
            moveto.z = pos[2]
            
        id = uuid.uuid4()
        classname = inspect.stack()[1][0].f_locals['self'].__class__.__name__
        task = Task(id, moveto, classname, beforeCallBack, CallBack, args)
        # bebag print(vars(task))
        
        #position = self.sortmanage.getPosition(getTasks(),task)
        self.__tasks.insert(0, task)
        return id
    def delTask(force = False):
        pass

    def getCurentTask(self):
        return self.__curentTask
    def TaskLoop(self):
        while 1:
            while len(self.__tasks) > 0:

                self.__curentTask = self.__tasks.pop(0)

                if self.__curentTask.args is not None:
                    args = self.__curentTask.args
                else:
                    args = None
                
                if self.__curentTask.beforeCallBack is not None: 
                    self.__curentTask.beforeCallBack(*args)
                    
                print(self.__curentTask.id, "doing")
                print(self.__curentTask.moveto.x, self.__curentTask.moveto.y, self.__curentTask.moveto.z)
                self.robot._navigate_to_anchor(
                                                self.__curentTask.moveto.x, 
                                                self.__curentTask.moveto.y,
                                                self.__curentTask.moveto.z
                                                )
                
                self.__curentTask.CallBack(self.robot, *args)
                    
                print(self.__curentTask.id, "done")

            if self.robot.powerState:
                self.robot.powerControl(False)
            
             
