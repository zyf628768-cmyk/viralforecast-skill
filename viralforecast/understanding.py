"""Local object, temporal action, scene/copy and visible-expression inference."""
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image

from .common import ForecastError
from .media import binary
from .models import require

SCENES=["a person speaking to the camera", "a cooking demonstration", "a sports or fitness video",
        "a product demonstration", "a travel or outdoor scene", "an animal or pet", "a video game screen",
        "a music performance", "a landscape", "a text slide or graphic", "an abstract solid color image"]


def ranking(scores,labels,n=3,threshold=.4):
    values=np.asarray(scores,dtype=float)
    if values.ndim!=1 or len(values)!=len(labels) or not np.isfinite(values).all():
        raise ForecastError("Invalid model scores")
    order=values.argsort()[::-1][:n]
    return {"status":"candidate" if float(values[order[0]])>=threshold else "uncertain",
            "candidates":[{"label":str(labels[i]),"model_score":float(values[i])} for i in order],
            "score_interpretation":"model score, not a calibrated correctness or virality probability"}


def clip_frames(video,start,duration):
    args=[binary("ffmpeg"),"-nostdin","-v","error","-protocol_whitelist","file,pipe,crypto,data",
          "-ss",str(start),"-i",str(Path(video).resolve()),"-t",str(min(2,duration-start)),
          "-an","-vf","fps=8,scale=160:120","-frames:v","16","-pix_fmt","rgb24","-f","rawvideo","pipe:1"]
    try:
        p=subprocess.run(args,capture_output=True,timeout=60)
    except (OSError,subprocess.TimeoutExpired) as exc:
        raise ForecastError(f"Action clip extraction failed: {exc}") from exc
    if p.returncode or not p.stdout:
        raise ForecastError("No frames available for action recognition")
    frames=np.frombuffer(p.stdout,dtype=np.uint8).copy().reshape(-1,120,160,3)
    if len(frames)<16:
        frames=np.concatenate([frames,np.repeat(frames[-1:],16-len(frames),axis=0)])
    return frames


def understand(video,media,title,caption,directory,labels=None):
    labels=SCENES if labels is None else labels
    if not isinstance(labels,list) or not 2<=len(labels)<=64 or any(not isinstance(s,str) or not s.strip() or len(s)>200 for s in labels):
        raise ForecastError("Semantic labels must contain 2–64 nonempty strings, at most 200 characters each")
    paths,provenance={},{}
    for name in ("objects","actions","semantics","expression"):
        paths[name],provenance[name]=require(directory,name)
    try:
        import torch
        import cv2
        from torchvision.transforms.functional import pil_to_tensor
        from torchvision.models.detection import ssdlite320_mobilenet_v3_large, SSDLite320_MobileNet_V3_Large_Weights
        from torchvision.models.video import r3d_18,R3D_18_Weights
        from transformers import CLIPModel, CLIPProcessor, AutoImageProcessor, AutoModelForImageClassification
        torch.set_num_threads(4)
        ow=SSDLite320_MobileNet_V3_Large_Weights.DEFAULT
        detector=ssdlite320_mobilenet_v3_large(weights=None,weights_backbone=None).eval()
        detector.load_state_dict(torch.load(paths["objects"],map_location="cpu",weights_only=True))
        images=[]
        for f in media["keyframes"]:
            with Image.open(f["path"]) as im:
                images.append(im.convert("RGB"))
        objects=[]
        with torch.inference_mode():
            for f,im in zip(media["keyframes"],images):
                out=detector([ow.transforms()(im)])[0]
                detections=[{"label":ow.meta["categories"][int(label)],"model_score":float(score),
                             "box_xyxy":[float(x) for x in box]} for box,score,label in zip(out["boxes"],out["scores"],out["labels"]) if score>=.5]
                objects.append({"time":f["time"],"detections":detections[:20]})
        del detector
        aw=R3D_18_Weights.KINETICS400_V1
        action=r3d_18(weights=None).eval()
        action.load_state_dict(torch.load(paths["actions"],map_location="cpu",weights_only=True))
        actions=[]
        duration=media["duration_seconds"]
        with torch.inference_mode():
            for start in sorted(set([0,max(0,duration/2-1),max(0,duration-2)])):
                frames=torch.from_numpy(clip_frames(video,start,duration)).permute(0,3,1,2)
                scores=action(aw.transforms()(frames).unsqueeze(0)).softmax(-1)[0].numpy()
                actions.append({"start":start,"end":min(start+2,duration),**ranking(scores,aw.meta["categories"])})
        del action
        processor=CLIPProcessor.from_pretrained(paths["semantics"],local_files_only=True,use_fast=False)
        semantic=CLIPModel.from_pretrained(paths["semantics"],local_files_only=True).eval()
        with torch.inference_mode():
            inputs=processor(text=labels,images=images,return_tensors="pt",padding=True,truncation=True)
            scores=semantic(**inputs).logits_per_image.softmax(-1).numpy()
            scenes=[{"time":f["time"],**ranking(s,labels)} for f,s in zip(media["keyframes"],scores)]
            copy=(title+" "+caption).strip()
            alignment=None
            if copy:
                inputs=processor(text=[copy],images=images,return_tensors="pt",padding=True,truncation=True)
                out=semantic(**inputs)
                alignment={"cosine_similarity_by_frame":[float(x) for x in (out.image_embeds @ out.text_embeds.T)[:,0]],
                           "interpretation":"English-oriented CLIP similarity, not a calibrated relevance score; Chinese copy may be unreliable."}
        del semantic
        # Detect face regions first. Never classify an entire scene as a person's emotion.
        face_detector=cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
        if face_detector.empty():
            raise ForecastError("OpenCV face detector asset is unavailable")
        faces=[]
        for f,im in zip(media["keyframes"],images):
            for x,y,w,h in face_detector.detectMultiScale(cv2.cvtColor(np.asarray(im),cv2.COLOR_RGB2GRAY),scaleFactor=1.1,minNeighbors=5,minSize=(30,30))[:8]:
                faces.append((f["time"],[int(x),int(y),int(x+w),int(y+h)],im.crop((int(x),int(y),int(x+w),int(y+h)))))
        expressions=[]
        # Load and validate the actual model even for a no-face clip, but abstain on inference.
        ep=AutoImageProcessor.from_pretrained(paths["expression"],local_files_only=True,use_fast=False,trust_remote_code=False)
        emotion=AutoModelForImageClassification.from_pretrained(paths["expression"],local_files_only=True).eval()
        with torch.inference_mode():
            for t,box,crop in faces:
                values=emotion(**ep(images=crop,return_tensors="pt")).logits.softmax(-1)[0].numpy()
                names=[emotion.config.id2label[i] for i in range(len(values))]
                expressions.append({"time":t,"box_xyxy":box,**ranking(values,names,threshold=.6)})
        return {"status":"completed_local_models","objects":objects,"actions":actions,"scene_semantics":scenes,
                "copy_alignment":alignment,"expressions":{"status":"assessed" if expressions else "no_face_detected",
                                                             "faces":expressions,"interpretation":"visible facial expression cues only; never a person's true inner emotion"},
                "models":{k:{field:v for field,v in entry.items() if field in ('source','revision')} for k,entry in provenance.items()},
                "limitations":["Sparse sampled frames and clips may miss events. Closed-set models can misclassify unfamiliar scenes/actions.",
                                "Scores are not calibrated truth probabilities and do not enter the statistical forecasting model.",
                                "Facial expressions do not establish mood, intent, personality or mental health."]}
    except ImportError as exc:
        raise ForecastError('Vision dependencies missing; install .[understanding]') from exc
    except ForecastError:
        raise
    except Exception as exc:
        raise ForecastError(f"Local understanding failed: {exc}") from exc
