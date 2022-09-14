import json
import yaml
from pathlib import Path
from model.Settings import Settings
# import torch
# import torchvision
import numpy as np
import cv2
from time import time
import onnxruntime
from openvino.runtime import Core, get_batch, Layout

class AI():

    def __init__(self) -> None:
        self.w = Settings().resource_dir+"weights/"
        self.INPUT_WIDTH         = 640
        self.INPUT_HEIGHT        = 640
        self.SCORE_THRESHOLD     = 0.7
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
        self.half                = False
        self.airegion            = 0.25
        self.fixregion           = 1.5
        pass

    def letterbox(self, im, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleFill=False, scaleup=True, stride=32):
        # Resize and pad image while meeting stride-multiple constraints
        shape = im.shape[:2]  # current shape [height, width]
        if isinstance(new_shape, int):
            new_shape = (new_shape, new_shape)

        # Scale ratio (new / old)
        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
        if not scaleup:  # only scale down, do not scale up (for better val mAP)
            r = min(r, 1.0)

        # Compute padding
        ratio = r, r  # width, height ratios
        new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
        if auto:  # minimum rectangle
            dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding
        elif scaleFill:  # stretch
            dw, dh = 0.0, 0.0
            new_unpad = (new_shape[1], new_shape[0])
            ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # width, height ratios

        dw /= 2  # divide padding into 2 sides
        dh /= 2

        if shape[::-1] != new_unpad:  # resize
            im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
        return im, ratio, (dw, dh)

    def model(self,im):
        pass

    def non_max_suppression(self,
                            prediction,
                            conf_thres=0.25,
                            iou_thres=0.45,
                            classes=None,
                            agnostic=False,
                            multi_label=False,
                            labels=(),
                            max_det=300):
        """Non-Maximum Suppression (NMS) on inference results to reject overlapping bounding boxes

        Returns:
            list of detections, on (n,6) tensor per image [xyxy, conf, cls]
        """
        bs = prediction.shape[0]  # batch size
        nc = prediction.shape[2] - 5  # number of classes
        xc = prediction[..., 4] > conf_thres  # candidates

        # Checks
        assert 0 <= conf_thres <= 1, f'Invalid Confidence threshold {conf_thres}, valid values are between 0.0 and 1.0'
        assert 0 <= iou_thres <= 1, f'Invalid IoU {iou_thres}, valid values are between 0.0 and 1.0'

        # Settings
        # min_wh = 2  # (pixels) minimum box width and height
        max_wh = 7680  # (pixels) maximum box width and height
        max_nms = 30000  # maximum number of boxes into torchvision.ops.nms()
        time_limit = 0.3 + 0.03 * bs  # seconds to quit after
        redundant = True  # require redundant detections
        multi_label &= nc > 1  # multiple labels per box (adds 0.5ms/img)
        merge = False  # use merge-NMS

        t = time()
        output = [torch.zeros((0, 6), device=prediction.device)] * bs
        for xi, x in enumerate(prediction):  # image index, image inference
            # Apply constraints
            # x[((x[..., 2:4] < min_wh) | (x[..., 2:4] > max_wh)).any(1), 4] = 0  # width-height
            x = x[xc[xi]]  # confidence

            # Cat apriori labels if autolabelling
            if labels and len(labels[xi]):
                lb = labels[xi]
                v = torch.zeros((len(lb), nc + 5), device=x.device)
                v[:, :4] = lb[:, 1:5]  # box
                v[:, 4] = 1.0  # conf
                v[range(len(lb)), lb[:, 0].long() + 5] = 1.0  # cls
                x = torch.cat((x, v), 0)

            # If none remain process next image
            if not x.shape[0]:
                continue

            # Compute conf
            x[:, 5:] *= x[:, 4:5]  # conf = obj_conf * cls_conf

            # Box (center x, center y, width, height) to (x1, y1, x2, y2)
            box = self.xywh2xyxy(x[:, :4])

            # Detections matrix nx6 (xyxy, conf, cls)
            if multi_label:
                i, j = (x[:, 5:] > conf_thres).nonzero(as_tuple=False).T
                x = torch.cat((box[i], x[i, j + 5, None], j[:, None].float()), 1)
            else:  # best class only
                conf, j = x[:, 5:].max(1, keepdim=True)
                x = torch.cat((box, conf, j.float()), 1)[conf.view(-1) > conf_thres]

            # Filter by class
            if classes is not None:
                x = x[(x[:, 5:6] == torch.tensor(classes, device=x.device)).any(1)]

            # Apply finite constraint
            # if not torch.isfinite(x).all():
            #     x = x[torch.isfinite(x).all(1)]

            # Check shape
            n = x.shape[0]  # number of boxes
            if not n:  # no boxes
                continue
            elif n > max_nms:  # excess boxes
                x = x[x[:, 4].argsort(descending=True)[:max_nms]]  # sort by confidence

            # Batched NMS
            c = x[:, 5:6] * (0 if agnostic else max_wh)  # classes
            boxes, scores = x[:, :4] + c, x[:, 4]  # boxes (offset by class), scores
            i = torchvision.ops.nms(boxes, scores, iou_thres)  # NMS
            if i.shape[0] > max_det:  # limit detections
                i = i[:max_det]
            if merge and (1 < n < 3E3):  # Merge NMS (boxes merged using weighted mean)
                # update boxes as boxes(i,4) = weights(i,n) * boxes(n,4)
                iou = self.box_iou(boxes[i], boxes) > iou_thres  # iou matrix
                weights = iou * scores[None]  # box weights
                x[i, :4] = torch.mm(weights, x[:, :4]).float() / weights.sum(1, keepdim=True)  # merged boxes
                if redundant:
                    i = i[iou.sum(1) > 1]  # require redundancy

            output[xi] = x[i]
            if (time() - t) > time_limit:
                break  # time limit exceeded

        return output

    def scale_coords(self, img1_shape, coords, img0_shape, ratio_pad=None):
        # Rescale coords (xyxy) from img1_shape to img0_shape
        if ratio_pad is None:  # calculate from img0_shape
            gain = min(img1_shape[0] / img0_shape[0], img1_shape[1] / img0_shape[1])  # gain  = old / new
            pad = (img1_shape[1] - img0_shape[1] * gain) / 2, (img1_shape[0] - img0_shape[0] * gain) / 2  # wh padding
        else:
            gain = ratio_pad[0][0]
            pad = ratio_pad[1]

        coords[:, [0, 2]] -= pad[0]  # x padding
        coords[:, [1, 3]] -= pad[1]  # y padding
        coords[:, :4] /= gain
        self.clip_coords(coords, img0_shape)
        return coords

    def clip_coords(self,boxes, shape):
        # Clip bounding xyxy bounding boxes to image shape (height, width)
        if isinstance(boxes, torch.Tensor):  # faster individually
            boxes[:, 0].clamp_(0, shape[1])  # x1
            boxes[:, 1].clamp_(0, shape[0])  # y1
            boxes[:, 2].clamp_(0, shape[1])  # x2
            boxes[:, 3].clamp_(0, shape[0])  # y2
        else:  # np.array (faster grouped)
            boxes[:, [0, 2]] = boxes[:, [0, 2]].clip(0, shape[1])  # x1, x2
            boxes[:, [1, 3]] = boxes[:, [1, 3]].clip(0, shape[0])  # y1, y2

    def xyxy2xywh(self, x):
        # Convert nx4 boxes from [x1, y1, x2, y2] to [x, y, w, h] where xy1=top-left, xy2=bottom-right
        y = x.clone() if isinstance(x, torch.Tensor) else np.copy(x)
        y[:, 0] = (x[:, 0])   # x center
        y[:, 1] = (x[:, 1])   # y center
        y[:, 2] = x[:, 2] - x[:, 0]  # width
        y[:, 3] = x[:, 3] - x[:, 1]  # height
        return y

    def xywh2xyxy(self, x):
        # Convert nx4 boxes from [x, y, w, h] to [x1, y1, x2, y2] where xy1=top-left, xy2=bottom-right
        y = x.clone() if isinstance(x, torch.Tensor) else np.copy(x)
        y[:, 0] = x[:, 0] - x[:, 2] / 2  # top left x
        y[:, 1] = x[:, 1] - x[:, 3] / 2  # top left y
        y[:, 2] = x[:, 0] + x[:, 2] / 2  # bottom right x
        y[:, 3] = x[:, 1] + x[:, 3] / 2  # bottom right y
        return y

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

    def detect(self,im0):
        im0 = cv2.cvtColor(im0,cv2.COLOR_BGRA2BGR)
        im, im0 = self.circle_mask(im0)

        im = self.letterbox(im, self.INPUT_WIDTH, stride=self.stride, auto=False)[0]  # padded resize
        im = im.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
        im = np.ascontiguousarray(im)  # contiguous

        im = torch.from_numpy(im).to('cpu')
        im = im.half() if self.half else im.float()  # uint8 to fp16/32
        im /= 255  # 0 - 255 to 0.0 - 1.0
        if len(im.shape) == 3:
            im = im[None]  # expand for batch dim
        # Inference
        pred = self.model(im)

        pred = self.non_max_suppression(pred, self.CONFIDENCE_THRESHOLD, self.NMS_THRESHOLD)
        iboxs = []
        for i, det in enumerate(pred):  # per image
            s = ""

            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = self.scale_coords(im.shape[2:], det[:, :4], im0.shape).round()

                # Print results
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class
                    try:
                        s += f"{n} {self.names[int(c)]}{'s' * (n > 1)}, "  # add to string
                    except:
                        s += f"{n} {int(c)}{'s' * (n > 1)}, "  # add to string

                # Write results
                for *xyxy, conf, cls in reversed(det):
                    c = int(cls)  # integer class
                    try:
                        label =f'{self.names[c]} {conf:.2f}'
                    except:
                        label =f'{c} {conf:.2f}'
                    xywh = (self.xyxy2xywh(torch.tensor(xyxy).view(1, 4)) ).view(-1).tolist()  # normalized xywh
                    p1 = (int(xyxy[0].tolist()),int(xyxy[1].tolist()))
                    p2 = (int(xyxy[2].tolist()),int(xyxy[3].tolist()))
                    cv2.rectangle(im0, p1, p2, self.RED, self.THICKNESS)
                    cv2.putText(im0, label, p1, self.FONT_FACE, self.FONT_SCALE, self.YELLOW, self.THICKNESS, cv2.LINE_AA)

                    p1 = (int(xywh[0]-xywh[2]*(self.fixregion)), int(xywh[1]-xywh[3]*(self.fixregion)))
                    p2 = (int(xywh[0]+xywh[2]*(self.fixregion+1)), int(xywh[1]+xywh[3]*(self.fixregion+1)))
                    cv2.rectangle(im0, p1, p2, self.BLUE, self.THICKNESS)

                    iboxs.append(xywh)
        return im0,iboxs
    
class ORDML(AI):

    def __init__(self) -> None:
        super().__init__()

        options = onnxruntime.SessionOptions()
        options.enable_mem_pattern = False
        options.execution_mode = onnxruntime.ExecutionMode.ORT_SEQUENTIAL
        session = onnxruntime.InferenceSession(self.w+"best.onnx", providers=['DmlExecutionProvider'], sess_options=options)
        self.session = session
        meta = session.get_modelmeta().custom_metadata_map  # metadata
        if 'stride' in meta:
            self.stride, self.names = int(meta['stride']), eval(meta['names'])


    def model(self,im):
        b, ch, h, w = im.shape  # batch, channel, height, width
        if self.half and im.dtype != torch.float16:
            im = im.half()  # to FP16
        im = im.cpu().numpy()  # FP32
        y = self.session.run([self.session.get_outputs()[0].name], {self.session.get_inputs()[0].name: im})[0]
        if isinstance(y, np.ndarray):
            y = torch.tensor(y, device='cpu')
        return  y

class OVINO(AI):

    def __init__(self) -> None:
        super().__init__()
        self.device = "CPU"
        #VINO config
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
        b, ch, h, w = im.shape  # batch, channel, height, width
        if self.half and im.dtype != torch.float16:
            im = im.half()  # to FP16
        im = im.cpu().numpy()  # FP32
        y = self.executable_network([im])[self.output_layer]
        if isinstance(y, np.ndarray):
            y = torch.tensor(y, device=self.device.lower())
        return  y