from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
import aiofiles

from google.cloud import storage

from mmdeploy.apis.utils import build_task_processor
from mmdeploy.utils import get_input_shape, load_config
import torch


from mmengine.model import revert_sync_batchnorm
from mmseg.apis import inference_model, init_model, show_result_pyplot
from types import SimpleNamespace

import os
import io
from PIL import Image
import shutil
import datetime

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
      "http://localhost:3000", # this may have to be an env var
      "http://192.168.7.177:3000",
      "https://ai-demo-mobile-first.vercel.app",
      "http://ai-demo-mobile-first.vercel.app",
      "https://lila.vip",
      "https://www.lila.vip",
      "http://lila.vip",
      "http://www.lila.vip",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/segment/", response_class=HTMLResponse)
def handle_get_segment():
  # without the action attribute, form submits POST to same server, same path,  accept="image/jpeg"
  return """
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data> 
      <input type=file name=image>
      <select name=model>
        <option value=pspnet>PSPnet</option>
        <option value=segformer>Segformer</option>
      </select>
      <input type=submit value=Upload>
    </form>
  """

def segmentImgSEGFORMER(curr):
  args = {
    "img": f"images/input_M{curr}.png",
    "config": "mmsegmentation/configs/segformer/segformer_mit-b0_8xb2-160k_foodwaste-512x512.py",
    "checkpoint": "segformer.pth",
    "out_file": f"segformer_result_M{curr}M.png",
    "device": "cpu",
    "opacity": 0.5,
    "title": "result"
  }
  args = SimpleNamespace(**args)

  # build the model from a config file and a checkpoint file
  model = init_model(args.config, args.checkpoint, device=args.device)
  if args.device == 'cpu':
      model = revert_sync_batchnorm(model)
  # test a single image
  result = inference_model(model, args.img)
  # show the results
  show_result_pyplot(
      model,
      args.img,
      result,
      title=args.title,
      opacity=args.opacity,
      draw_gt=False,
      show=False if args.out_file is not None else True,
      out_file=args.out_file)
  
  # save a mask
  show_result_pyplot(
    model,
    args.img,
    result,
    title=args.title,
    opacity=1,
    draw_gt=False,
    show=False if args.out_file is not None else True,
    out_file='./mask.png')
  
  client = storage.Client()
  bucket = client.get_bucket("lila-ai-demo-api-server")
  blob = bucket.blob(args.out_file)
  blob.upload_from_filename("./" + args.out_file)

  return args.out_file

def segmentImgPSPNET(curr):
  args = {
    "img": f"images/input_M{curr}.png",
    "config": "mmsegmentation/configs/pspnet/pspnet_r50-d8_80k_foodwaste.py",
    "checkpoint": "PSPNet.pth",
    "out_file": f"pspnet_result_M{curr}M.png",
    "device": "cpu",
    "opacity": 0.5,
    "title": "result"
  }
  args = SimpleNamespace(**args)

  # build the model from a config file and a checkpoint file
  model = init_model(args.config, args.checkpoint, device=args.device)
  if args.device == 'cpu':
      model = revert_sync_batchnorm(model)
  # test a single image
  result = inference_model(model, args.img)
  # show the results
  show_result_pyplot(
      model,
      args.img,
      result,
      title=args.title,
      opacity=args.opacity,
      draw_gt=False,
      show=False if args.out_file is not None else True,
      out_file=args.out_file)
  
  # save a mask
  show_result_pyplot(
    model,
    args.img,
    result,
    title=args.title,
    opacity=1,
    draw_gt=False,
    show=False if args.out_file is not None else True,
    out_file='./mask.png')
  
  client = storage.Client()
  bucket = client.get_bucket("lila-ai-demo-api-server")
  blob = bucket.blob(args.out_file)
  blob.upload_from_filename("./" + args.out_file)

  return args.out_file


def calcColorFrac(image, color):
  width, height = image.size
  target_r, target_g, target_b = color
  matching_pixels = 0

  pixel_data = image.load()  # Load pixel data for faster access

  for y in range(height):
    for x in range(width):
      pixel_color = pixel_data[x, y]
      r, g, b, _ = pixel_color  # PNG images have an extra alpha channel

      if r == target_r and g == target_g and b == target_b:
        matching_pixels += 1

  total_pixels = width * height
  color_fraction = matching_pixels / total_pixels
  return color_fraction

def calcNPK():
  colorMap = {
    'background': [0, 0, 0],
    'Banana skin': [255, 255, 0],
    'Egg shell': [255, 255, 255],
    'Lettuce leaf': [146, 208, 80],
    'Hard bread': [131, 60, 12],
    'Cooked meat': [160, 121, 191],
    'Onion skin': [183, 123, 104],
    'Potato skin': [153, 76, 0],
    'apple core': [255, 0, 0],
    'Orange': [237, 125, 49],
    'Waffle': [255, 192, 0],
    'Apple peel': [192, 0, 0],
    'Corn leaves': [153, 153, 0],
    'cucumber': [68, 84, 106],
    'grape': [153, 0, 153],
    'Orange skin': [255, 178, 102],
    'Tea bag': [102, 51, 0],
    'Avocado skin': [102, 255, 178],
    'Chicken bone': [102, 102, 0],
    'Cooked fish': [91, 155, 213]
  }
  
  # in cm
  thicknessMap = {
  'Banana skin': 0.5, 
  'Egg shell': 0.15, 
  'Lettuce leaf': 1, 
  'Hard bread': 1.25, 
  'Cooked meat': 2, 
  'Onion skin': 0.08, 
  'Potato skin': 0.12, 
  'apple core': 3.5, 
  'Orange': 6, 
  'Waffle': 1.2, 
  'Apple peel': 0.15, 
  'Corn leaves': 0.7, 
  'cucumber': 2, 
  'grape': 1.5, 
  'Orange skin': 0.8, 
  'Tea bag': 0.6, 
  'Avocado skin': 0.2, 
  'Chicken bone': 0.06, 
  'Cooked fish': 2
  }
  
  # in g/cc
  densityMap = {
  'Banana skin': 4.392,
  'Egg shell': 2.386,
  'Lettuce leaf': 0.24,
  'Hard bread': 0.25,
  'Cooked meat': 1.033,
  'Onion skin': 0.5,
  'Potato skin': 0.47,
  'apple core': 0.53,
  'Orange': 1.3,
  'Waffle': 0.9,
  'Apple peel': 0.4,
  'Corn leaves': 0.08161,
  'cucumber': 1,
  'grape': 0.64,
  'Orange skin': 0.41,
  'Tea bag': 0.41,
  'Avocado skin': 1.035,
  'Chicken bone': 1.85,
  'Cooked fish': 0.57
}
  
  # in mg per 100g
  npkMap = {
    'Banana skin': [443.75, 100, 420],
    'Egg shell': [350, 160, 150],
    'Lettuce leaf': [180, 27, 91],
    'Hard bread': [1970, 212, 250],
    'Cooked meat': [3260, 280, 476],
    'Onion skin': [431.25, 300.36, 161.2],
    'Potato skin': [3152, 262.2, 287.14],
    'apple core': [25, 10, 110],
    'Orange': [50, 22, 159],
    'Waffle': [375, 381, 177],
    'Apple peel': [12.5, 12, 257.57],
    'Corn leaves': [300, 36, 262],
    'cucumber': [50, 36, 200],
    'grape': [150, 25, 229],
    'Orange skin': [93.75, 21, 212],
    'Tea bag': [4160, 650, 2000],
    'Avocado skin': [1100, 141, 459],
    'Chicken bone': [646.875, 2040, 40],
    'Cooked fish': [1381.25, 252, 384]
  }

  mask = Image.open("./mask.png")
  mask = mask.convert("RGBA")

  n = 0
  p = 0
  k = 0

  # HANDLE BG CLASS SEPARATELY

  w, h = mask.size
  area = (100) * ((h/w) * 100) # assuming w is 1m let's say, and we get area in cm^2

  for key in colorMap:
    if key == "background":
      continue

    f = calcColorFrac(mask, colorMap[key])
    volume = area * f * thicknessMap[key] # in cc
    mass = volume * densityMap[key]

    # print(f"{key} contribution: n - {npkMap[key][0] * (mass/100)}, p - {npkMap[key][1] * (mass/100)}, k - {npkMap[key][2] * (mass/100)}")

    n += npkMap[key][0] * (mass/100)
    p += npkMap[key][1] * (mass/100)
    k += npkMap[key][2] * (mass/100)

  p /= n
  k /= n
  n /= n # this must b last so that p & k r divided by old n value

  return n, p, k

@app.post("/segment/")
async def handle_post_segment(image: UploadFile, model: str = Form("pspnet")):
  curr = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")

  inputName = f"input_M{curr}.png"
  data = await image.read()
  img = Image.open(io.BytesIO(data))

  convBuffer = io.BytesIO()
  img.save(convBuffer, format="png")
  convData = convBuffer.getvalue()

  async with aiofiles.open("images/" + inputName, "wb") as f:
    await f.write(convData)

  client = storage.Client()
  bucket = client.get_bucket("lila-ai-demo-submitted-images")
  blob = bucket.blob(inputName)
  blob.upload_from_filename("./images/" + inputName, content_type="image/png")
  
  outFile = ""
  if model == "pspnet":
    outFile = segmentImgPSPNET(curr)
  elif model == "segformer":
    outFile = segmentImgSEGFORMER(curr)

  NPK = calcNPK()

  return {"status": "OK",
          "N": NPK[0],
          "P": NPK[1],
          "K": NPK[2],
          "resultPath": f"/results/{outFile}"}

@app.get("/results/{img}")
async def get_image(img: str):
  client = storage.Client()
  bucket_name = "lila-ai-demo-api-server"
  bucket = client.get_bucket(bucket_name)
  blob = bucket.blob(img)
  image_bytes = blob.download_as_bytes()

  return Response(content=image_bytes, media_type="image/png")  

