'''
状态
'''
import queue
import tempfile
import threading

from model.Weapon import Weapon

class Status:

    #weapon
    weapon:Weapon = Weapon()

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

    def change_weapon(self, weapon:int):
        if self.weapon != weapon:
            self.weapon = weapon

        return self.weapon1

    def no_weapon(self):
        if self.weapon != None:
            self.weapon = Weapon()
            self.write_config()

    def change_fix(self,x,y):
        if (self.x != x or self.y!=y):
            self.x = x
            self.y = y
            self.write_config()

    def write_config(self,msg:str="",consoleshow:bool=False):
        config_content = ""

        if self.weapon and self.weapon.weapon_name:
            weaponname = self.weapon.weapon_name
        else:
            weaponname = 'none'

        config_content += "rweapon=\"{}\"\n".format(weaponname)


        config_content += "rx={}\n".format(self.x)
        config_content += "ry={}\n".format(self.y)

        if consoleshow:
            print("=== {} ===".format(msg))
            print(config_content)
            print("==========")

        with open(self.config_file, 'w') as f:
            f.write(config_content)
