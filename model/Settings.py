import json
import threading
import traceback

from myutils.QtUtils import appexit, message_critical

class Settings:

    _instance_lock=threading.Lock()

    app_config_path = "./config.json"

    resource_dir = ""

    def __init__(self) -> None:
        '''
        初始化
        '''

    def __new__(cls, *args, **kwargs):
        if not hasattr(Settings, "_instance"):
            with Settings._instance_lock:
                if not hasattr(Settings, "_instance"):
                    Settings._instance = object.__new__(cls)
                    Settings._instance.load_app_config()
                    Settings._instance.load_config()
        return Settings._instance
    

    def load_app_config(self):
        try:
            with open(self.app_config_path, "r") as f:
                app_config = json.load(f)
                self.app_config = app_config
                self.resource_dir = "./resource/{}/".format(app_config["game"])
        except:
            self.app_config = {
                "monitor": 1,
                "game": "PUBG",
                "commit1": "",
                "commit2": "",
                "update": "GITHUB"
            }
            self.resource_dir = "./resource/PUBG/"
            self.save_app_config_to_json()
    
    def load_config(self):

        self.config_path = "./resource/{}/config.json".format(self.app_config["game"])

        try:
            with open(self.config_path, "r") as f:
                config = json.load(f)
                self.config = config
        except Exception as e:
            traceback.print_exc()

    def get_config(self,name):
        if not name in self.config.keys():
            self.config[name] = {}
        return self.config[name]

    def save_config_to_json(self):
        try:
            with open(self.config_path, "w") as f:
                json.dump(self.config,f,indent=4)
            print("CONFIG SAVED")
        except:
            pass

    def save_app_config_to_json(self):
        try:
            with open(self.app_config_path, "w") as f:
                json.dump(self.app_config,f,indent=4)
            print("APP CONFIG SAVED")
        except Exception as e:
            traceback.print_exc()
            pass
    
    def change_game(self,game):
        self.app_config["game"] = game
        self.resource_dir = "./resource/{}/".format(game)
        self.load_config()