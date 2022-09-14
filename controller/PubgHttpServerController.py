import os
import base64
from pathlib import Path
from datetime import datetime
from time import sleep
from model.Settings import Settings
from model.Status import Status

from flask import Flask,request,render_template,send_file
from flask_socketio import SocketIO
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot,QThread

from myutils.QtUtils import start_q_thread

status = Status()
pwd = os.getcwd().replace("\\","/")
imgcache = {}

class StartWebServer(QObject):

    start = pyqtSignal(bool)

    def __init__(self,socketio,app) -> None:
        super().__init__()
        self.socketio = socketio
        self.app = app
        self.start.connect(self.rec)

    @pyqtSlot(bool)
    def rec(self, run):
        print("server started")
        self.socketio.run(self.app,host="0.0.0.0",port=5000)


class WebApp(QObject):
    app = Flask(__name__, template_folder=os.path.abspath(Settings().resource_dir+"flaskr/"))
    socketio = SocketIO(app)
    start = pyqtSignal(bool)
    webserver = StartWebServer(socketio,app)
    updateQueue = status.updateQueue
    clients = []
    initclients = []

    def __init__(self) -> None:
        super().__init__()
        self.start.connect(self.rec)
        self.init_img_cache()

        self.thread = QThread(parent=self)

        self.webserver.moveToThread(self.thread)
        self.webserver.start.emit(True)
        self.thread.start()
    
    def init_img_cache(self):
        d = pwd+Settings().resource_dir
        for file in Path(d).rglob("*.png"):
            with open (file,'rb') as f:
                file = os.path.abspath(str(file))
                base64_data=base64.b64encode(f.read())
                s=base64_data.decode()
                data='data:image/jpeg;base64,%s'%s
                imgcache[str(file)] = data

    @app.route("/")
    def hello_world():
        return render_template("index.html")

    @socketio.on('connect')
    def handle_connect():
        print("网页连接",request.sid)
        WebApp.clients.append(request.sid)
        WebApp.initclients.append(request.sid)

    @socketio.on('disconnect')
    def handle_disconnect():
        print("网页断开",request.sid)
        WebApp.clients.remove(request.sid)

    def send_message(self,client_id,taskname):
        print(f"{client_id}-{taskname}")
        if taskname == "changeweapon":
            self.socketio.emit("update", [taskname,status.weapon], room=client_id)
        elif taskname == "pose":
            pose = status.pose
            if pose == None:
                file = os.path.abspath(pwd+Settings().resource_dir+"pose_null.png")
            else:
                file = os.path.abspath(pwd+Settings().resource_dir+"pos/{}.png".format(pose))
            self.socketio.emit('update', [taskname, imgcache[file]], room=client_id)
        elif taskname == "weapon1":
            weapon = status.weapon1
            if not weapon.weapon_name:
                file = os.path.abspath(pwd+Settings().resource_dir+"weapon_null.png")
            else:
                file = os.path.abspath(pwd+"/{}".format(weapon.get_weapon_img_path()))
            self.socketio.emit('update', [taskname, imgcache[file]], room=client_id)
        elif taskname == "weapon2":
            weapon = status.weapon2
            if not weapon.weapon_name:
                file = os.path.abspath(pwd+Settings().resource_dir+"/weapon_null.png")
            else:
                file = os.path.abspath(pwd+"/{}".format(weapon.get_weapon_img_path()))
            self.socketio.emit('update', [taskname, imgcache[file]], room=client_id)
        elif taskname == "attachment":
            resultall = []
            weapon1 = status.weapon1
            weapon2 = status.weapon2
            for i in [weapon1,weapon2]:
                result = []
                scope = os.path.abspath(pwd+"/{}".format(i.get_scope_img_path()))
                a1 = os.path.abspath(pwd+"/{}".format(i.get_a1_img_path()))
                a2 = os.path.abspath(pwd+"/{}".format(i.get_a2_img_path()))
                a3 = os.path.abspath(pwd+"/{}".format(i.get_a3_img_path()))
                a4 = os.path.abspath(pwd+"/{}".format(i.get_a4_img_path()))
                result.append(imgcache[scope])
                result.append(imgcache[a1])
                result.append(imgcache[a2])
                result.append(imgcache[a3])
                result.append(imgcache[a4])
                resultall.append(result)

            self.socketio.emit('update', [taskname, resultall], room=client_id)
    
    @pyqtSlot(bool)
    def rec(self, run):
        if run:
            self.webserver.start.emit(True)
            while True:
                # for clientid in self.clients:
                #     self.send_message(clientid,"weapon1")
                #     self.send_message(clientid,"weapon2")
                #     self.send_message(clientid,"attachment")
                #     self.send_message(clientid,"pose")
                #     sleep(1)

                if len(self.initclients) > 0:
                    for clientid in self.initclients:
                        self.send_message(clientid,"changeweapon")
                        self.send_message(clientid,"pose")
                        self.send_message(clientid,"weapon1")
                        self.send_message(clientid,"weapon2")
                        self.send_message(clientid,"attachment")
                    self.initclients.clear()

                try:
                    taskname = self.updateQueue.get(block=False,timeout=0)
                    if taskname:
                        for clientid in self.clients:
                            self.send_message(clientid,taskname)
                except Exception as e:
                    pass
                sleep(0.01)
                
class HttpServerController:

    def __init__(self,view) -> None:
        self.view = view

        self.start_server()
        
    def start_server(self):
        address = self.get_ip_addess()
        self.view.set_url_link("<b>手机浏览器打开<b><br><a href=\"http://{}:5000\">http://{}:5000/".format(address, address))

        self.webapp = WebApp()
        self.thread = start_q_thread(self.view,self.webapp)

    def get_ip_addess(self):
        try:
            if "nt" == os.name:
                address = [a for a in os.popen('route print').readlines() if ' 0.0.0.0 ' in a][0].split()[-2]
            else:
                address = os.popen("dev=$(ip route | grep default | awk '{print $5}');ip -4 addr show $dev | grep inet | awk '{print $2}' | awk -F/ '{print $1}'").readlines()[0]
        except:
            return "0.0.0.0"

        return address.strip()