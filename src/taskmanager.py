#from sortmanager import SortManager
import inspect
import uuid

class Task():
    def __init__(self, id, classname, beforeCallBack, CallBack, args):
        self.id = id
        self.className = classname
        self.beforeCallBack = beforeCallBack
        self.CallBack = CallBack
        self.args = args
        
class TaskManager():
    def __init__(self):
        self.__tasks = []
        self.__curentTask = None
        
        #self.sortmanager = SortManager()

    def getTasks(self):
        return self.__tasks
         
    def addTask(self, priority, pos, CallBack, beforeCallBack=None, *args):
        #check and get posision of task
        id = uuid.uuid4()
        classname = inspect.stack()[1][0].f_locals['self'].__class__.__name__
        task = Task(id,classname, beforeCallBack, CallBack, args)
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
                
                self.__curentTask.CallBack(*args)
                    
                print(self.__curentTask.id, "done")
            
             
