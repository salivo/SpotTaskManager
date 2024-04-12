
class SortManager():
    def __init__(self):
        pass
        
    def getTaskInsertPos(self, tasks_list, task):
        for i, j in enum(tasks_list):
            if task.priority > j.priority:
                return i
        return -1

    def getNextTaskPos(self, task_list):
        return 0
