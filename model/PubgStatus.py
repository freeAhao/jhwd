'''
状态
'''
import queue
import tempfile
import threading

from model.Weapon import Weapon

class Status:

    #pose
    pose = None
    #weapon
    weapon:int = None
    weapon1:Weapon = Weapon()
    weapon2:Weapon = Weapon()

    updateQueue = queue.Queue()

    #fix
    x = 0
    y = 0

    # qt_comunicate = qt_comunicate
    config_file =  tempfile.gettempdir() + "/x.lua"
    _instance_lock=threading.Lock()

    '''
    Pose状态
    '''
    def __init__(self) -> None:
        '''
        初始化
        '''
        pass

    def __new__(cls, *args, **kwargs):
        if not hasattr(Status, "_instance"):
            with Status._instance_lock:
                if not hasattr(Status, "_instance"):
                    Status._instance = object.__new__(cls)
        return Status._instance

    def change_pose(self, pose):
        if self.pose != pose:
            self.pose = pose

    def change_weapon(self, weapon:int):
        if self.weapon != weapon:
            self.weapon = weapon

        if weapon == 1:
            return self.weapon1
        if weapon == 2:
            return self.weapon2

    def no_weapon(self):
        if self.weapon != None:
            self.weapon = None
            self.write_config()

    def no_pose(self):
        if self.pose != None:
            self.pose = None
            self.write_config()

    def change_fix(self,x,y):
        if (self.x != x or self.y!=y):
            self.x = x
            self.y = y
            self.write_config()

    def set_default_attachment(self,attachment):
        self.defaultattachment = attachment

    def change_attachment(self,attachments):
        write = False 
        for i,attachment in enumerate(attachments):
            for index,value in enumerate(attachment):
                if value == 0:
                    attachments[i][index] = self.defaultattachment[index]

        if self.attachment1 != attachments[0]:
            self.attachment1 = attachments[0]
            write = True

        if self.attachment2 != attachments[1]:
            self.attachment2 = attachments[1]
            write = True

        if write:
            self.updateQueue.put("attachment")
            self.write_config("attachment update",True)

    def write_config(self,msg:str="",consoleshow:bool=False):
        config_content = ""

        if self.weapon==1 and self.weapon1:
            weaponname = self.weapon1.weapon_name
        elif self.weapon==2 and self.weapon2:
            weaponname = self.weapon2.weapon_name
        else:
            weaponname = 'none'

        config_content += "rweapon=\"{}\"\n".format(weaponname)

        config_content += "rpose={}\n".format(self.pose if self.pose else 1)

        config_content += "rx={}\n".format(self.x)
        config_content += "ry={}\n".format(self.y)

        if self.weapon == 1: 
            config_content += "rscope={}\n".format(self.weapon1.scope if self.weapon1.scope else 1)
            config_content += "rattachment2={}\n".format(self.weapon1.a1 if self.weapon1.scope else 1)
            config_content += "rattachment3={}\n".format(self.weapon1.a2 if self.weapon1.scope else 1)
            config_content += "rattachment4={}\n".format(self.weapon1.a3 if self.weapon1.scope else 1)
            config_content += "rattachment5={}\n".format(self.weapon1.a4 if self.weapon1.scope else 1)
        elif self.weapon == 2:
            config_content += "rscope={}\n".format(self.weapon2.scope if self.weapon2.scope else 1)
            config_content += "rattachment2={}\n".format(self.weapon2.a1 if self.weapon2.scope else 1)
            config_content += "rattachment3={}\n".format(self.weapon2.a2 if self.weapon2.scope else 1)
            config_content += "rattachment4={}\n".format(self.weapon2.a3 if self.weapon2.scope else 1)
            config_content += "rattachment5={}\n".format(self.weapon2.a4 if self.weapon2.scope else 1)
        else:
            config_content += "rscope={}\n".format(self.weapon1.scope if self.weapon1.scope else 1)
            config_content += "rattachment2={}\n".format(self.weapon1.a1 if self.weapon1.scope else 1)
            config_content += "rattachment3={}\n".format(self.weapon1.a2 if self.weapon1.scope else 1)
            config_content += "rattachment4={}\n".format(self.weapon1.a3 if self.weapon1.scope else 1)
            config_content += "rattachment5={}\n".format(self.weapon1.a4 if self.weapon1.scope else 1)

        if consoleshow:
            print("=== {} ===".format(msg))
            print(config_content)
            print("==========")

        with open(self.config_file, 'w') as f:
            f.write(config_content)
