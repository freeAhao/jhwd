from collections import namedtuple,OrderedDict
import yaml
from pathlib import Path
import numpy as np
import cv2
from time import time
import pip

from model.Settings import Settings

class AI():

    def __init__(self) -> None:
        self.w = Settings().resource_dir+"weights/"
        self.INPUT_WIDTH         = 640
        self.INPUT_HEIGHT        = 640
        self.SCORE_THRESHOLD     = 0.4
        self.NMS_THRESHOLD       = 0.4
        self.CONFIDENCE_THRESHOLD= 0.4
        self.FONT_FACE           = cv2.FONT_HERSHEY_SIMPLEX
        self.FONT_SCALE          = 0.7
        self.THICKNESS           = 1
        self.fontSize            = 0.3
        # Colors
        self.BLACK               = (0,0,0)
        self.BLUE                = (255,178,50)
        self.YELLOW              = (0,255,255)
        self.RED                 = (0,0,255)
        self.fp16                = False
        self.airegion            = 0.25
        self.fixregion           = 1.5

    def model(self,im):
        pass

    def circle_mask(self,img0):
        img = img0.copy()
        center = (round(img.shape[0]/2),round(img.shape[0]/2))

        length = round(img.shape[0]*self.airegion)

        mask = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)
        cv2.circle(mask, center, length,(255,255,255),-1)
        # axes = (length, length)
        # angle = 0
        # startAngle = 180
        # endAngle = 360
        # cv2.ellipse(mask, center, axes, angle, startAngle, endAngle, (255,255,255), -1)
        img = cv2.add(img, np.zeros(np.shape(img), dtype=np.uint8), mask=mask)
        img0 = cv2.circle(img0, center, length,(255,255,255),2)
        # img0 = cv2.ellipse(img0, center, axes, angle, startAngle, endAngle, (255,255,255), 2)
        return img, img0

    def resize_image(self, srcimg, keep_ratio=True):
        top, left, newh, neww = 0, 0, self.INPUT_HEIGHT, self.INPUT_WIDTH
        if keep_ratio and srcimg.shape[0] != srcimg.shape[1]:
            hw_scale = srcimg.shape[0] / srcimg.shape[1]
            if hw_scale > 1:
                newh, neww = self.INPUT_HEIGHT, int(self.INPUT_WIDTH / hw_scale)
                img = cv2.resize(srcimg, (neww, newh), interpolation=cv2.INTER_AREA)
                left = int((self.INPUT_WIDTH - neww) * 0.5)
                img = cv2.copyMakeBorder(img, 0, 0, left, self.INPUT_WIDTH - neww - left, cv2.BORDER_CONSTANT,
                                         value=0)  # add border
            else:
                newh, neww = int(self.INPUT_HEIGHT * hw_scale), self.INPUT_WIDTH
                img = cv2.resize(srcimg, (neww, newh), interpolation=cv2.INTER_AREA)
                top = int((self.INPUT_HEIGHT - newh) * 0.5)
                img = cv2.copyMakeBorder(img, top, self.INPUT_HEIGHT - newh - top, 0, 0, cv2.BORDER_CONSTANT, value=0)
        else:
            img = cv2.resize(srcimg, (self.INPUT_HEIGHT,self.INPUT_WIDTH), interpolation=cv2.INTER_AREA)
        return img, newh, neww, top, left

    def postprocess(self, frame, outs, pad_hw):
        newh, neww, padh, padw = pad_hw
        frameHeight = frame.shape[0]
        frameWidth = frame.shape[1]
        ratioh, ratiow = frameHeight / newh, frameWidth / neww
        # Scan through all the bounding boxes output from the network and keep only the
        # ones with high confidence scores. Assign the box's class label as the class with the highest score.
        classIds = []
        confidences = []
        boxes = []
        for detection in outs[np.where(outs[:,4]>self.SCORE_THRESHOLD)]:
            scores = detection[5:]
            classId = np.argmax(scores)
            confidence = scores[classId]
            # confidence = detection[5]
            if not confidence > self.CONFIDENCE_THRESHOLD:
                continue
            center_x = int((detection[0] - padw) * ratiow)
            center_y = int((detection[1] - padh) * ratioh)
            width = int(detection[2] * ratiow)
            height = int(detection[3] * ratioh)
            left = int(center_x - width / 2)
            top = int(center_y - height / 2)
            classIds.append(classId)
            confidence = detection[4]
            confidences.append(float(confidence))
            boxes.append([left, top, width, height])
        # Perform non maximum suppression to eliminate redundant overlapping boxes with
        # lower confidences.
        indices = cv2.dnn.NMSBoxes(boxes, confidences, self.CONFIDENCE_THRESHOLD, self.NMS_THRESHOLD)
        iboxs = []
        for i in indices:
            i = i[0] if isinstance(i, (tuple,list)) else i
            box = boxes[i]
            left = box[0]
            top = box[1]
            width = box[2]
            height = box[3]
            frame = self.drawPred(frame, classIds[i], confidences[i], left, top, left + width, top + height)
            iboxs.append([left,top,width,height])
        return frame,iboxs

    def drawPred(self, frame, classId, conf, left, top, right, bottom):

        c = int(classId)  # integer class
        try:
            label =f'{self.names[c]} {conf:.2f}'
        except:
            label =f'{c} {conf:.2f}'
        # Draw a bounding box.
        cv2.rectangle(frame, (left, top), (right, bottom), self.RED, self.THICKNESS)
        cv2.putText(frame, label, (left, top), self.FONT_FACE, self.FONT_SCALE, self.YELLOW, self.THICKNESS,cv2.LINE_AA)

        il,it,iw,ih = (
            left,
            top,
            right-left,
            bottom-top,
        )
        op1 = (
            int(il-self.fixregion/2*iw),
            int(it-self.fixregion/3*ih),
        )
        op2 = (
            int(il+iw+self.fixregion/2*iw),
            int(it+ih+self.fixregion/3*ih),
        )
        cv2.rectangle(frame, op1, op2, self.BLUE, self.THICKNESS)

        return frame

    def detect(self,im0):
        im0 = cv2.cvtColor(im0,cv2.COLOR_BGRA2BGR)
        im, im0 = self.circle_mask(im0)
        im, newh, neww, top, left = self.resize_image(im)
        im = im.astype(np.float32) / 255.0
        im = np.expand_dims(np.transpose(im, (2, 0, 1)), axis=0)

        outs = self.model(im)
        im,iboxs = self.postprocess(im0, outs, (newh, neww, top, left))
        return im,iboxs
    
class ORDML(AI):

    providers={
        "DmlExecutionProvider": "onnxruntime-directml",
        "CPUExecutionProvider": "onnxruntime",
        "CUDAExecutionProvider": "onnxruntime-gpu"
    }

    def __init__(self,provider) -> None:
        super().__init__()
        try:
            import onnxruntime
        except:
            raise Exception("onnxruntime not found")

        if provider=="DmlExecutionProvider":
            options = onnxruntime.SessionOptions()
            options.enable_mem_pattern = False
            options.execution_mode = onnxruntime.ExecutionMode.ORT_SEQUENTIAL
            session = onnxruntime.InferenceSession(self.w+"best.onnx", providers=['DmlExecutionProvider','CPUExecutionProvider'], sess_options=options)
        elif provider=="CPUExecutionProvider":
            options = onnxruntime.SessionOptions()
            session = onnxruntime.InferenceSession(self.w+"best.onnx", providers=['CPUExecutionProvider'], sess_options=options)
        elif provider=="CUDAExecutionProvider":
            options = onnxruntime.SessionOptions()
            session = onnxruntime.InferenceSession(self.w+"best.onnx", providers=['CUDAExecutionProvider','CPUExecutionProvider'], sess_options=options)
        
        self.session = session
        meta = session.get_modelmeta().custom_metadata_map  # metadata
        if 'stride' in meta:
            self.stride, self.names = int(meta['stride']), eval(meta['names'])


    def model(self,im):
        res = self.session.run([self.session.get_outputs()[0].name], {self.session.get_inputs()[0].name: im})[0].squeeze(axis=0)
        return res

class OVINO(AI):

    def __init__(self) -> None:
        super().__init__()
        self.device = "CPU"
        #VINO config
        try:
            from openvino.runtime import Core, get_batch, Layout
        except:
            return
        ie = Core()
        if not Path(self.w).is_file():  # if not *.xml
            w = next(Path(self.w).glob('*.xml'))  # get *.xml file from *_openvino_model dir
        network = ie.read_model(model=self.w+"best.xml", weights=Path(self.w+"best.xml").with_suffix('.bin'))
        if network.get_parameters()[0].get_layout().empty:
            network.get_parameters()[0].set_layout(Layout("NCHW"))
        batch_dim = get_batch(network)
        if batch_dim.is_static:
            batch_size = batch_dim.get_length()
        executable_network = ie.compile_model(network, device_name=self.device)  # device_name="MYRIAD" for Intel NCS2
        self.executable_network =  executable_network
        self.output_layer = next(iter(executable_network.outputs))
        meta = Path(w).with_suffix('.yaml')
        if meta.exists():
            self.stride, self.names = self._load_metadata(meta)  # load metadata

    @staticmethod
    def yaml_load(file='data.yaml'):
        # Single-line safe yaml loading
        with open(file, errors='ignore') as f:
            return yaml.safe_load(f)

    @staticmethod
    def _load_metadata(f='path/to/meta.yaml'):
        # Load metadata from meta.yaml if it exists
        d = OVINO.yaml_load(f)
        return d['stride'], d['names']  # assign stride, names

    def model(self,im):
        y = self.executable_network([im])[self.output_layer][0]
        return  y
