from fastapi import FastAPI, UploadFile, BackgroundTasks
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
import aiofiles

from google.cloud import storage

from mmdeploy.apis.utils import build_task_processor
from mmdeploy.utils import get_input_shape, load_config
import torch

import os
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
      <input type=submit value=Upload>
    </form>
  """

def segmentImg(curr):
  deploy_cfg = './mmdeploy/configs/mmseg/segmentation_onnxruntime_dynamic.py'
  model_cfg = './mmsegmentation/configs/pspnet/pspnet_r50-d8_80k_foodwaste.py'
  device = 'cpu'
  backend_model = ['./dynamic_dir/onnx/pspnet/end2end.onnx']
  image = f"images/input_M{curr}"

  deploy_cfg, model_cfg = load_config(deploy_cfg, model_cfg)
  task_processor = build_task_processor(model_cfg, deploy_cfg, device)
  model = task_processor.build_backend_model(backend_model)

  input_shape = get_input_shape(deploy_cfg)
  model_inputs, _ = task_processor.create_input(image, input_shape)

  with torch.no_grad():
    result = model.test_step(model_inputs)

  task_processor.visualize( # for some reason this only saves to static folder on first time, after that it saves to root directory, so we manually move
    image=image,
    model=model,
    result=result[0],
    window_name='visualize',
    output_file=f'./result_M{curr}M.png')

  # then move the images to google cloud
  outputImg = f"result_M{curr}M_0.png"
  client = storage.Client()
  bucket = client.get_bucket("lila-ai-demo-api-server")
  blob = bucket.blob(outputImg)
  blob.upload_from_filename("./" + outputImg)

@app.post("/segment/")
async def handle_post_segment(image: UploadFile, bgTasks: BackgroundTasks):
  curr = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")

  inputImg = f"input_M{curr}"

  async with aiofiles.open("images/" + inputImg, "wb") as f:
    data = await image.read()
    await f.write(data)

  # we've saved the img but I need to interpret it as an image

  client = storage.Client()
  bucket = client.get_bucket("lila-ai-demo-submitted-images")
  blob = bucket.blob(inputImg)
  blob.upload_from_filename("./images/" + inputImg)
  
  segmentImg(curr)

  return {"status": "OK",
          "resultPath": f"/results/result_M{curr}M_0.png"}

@app.get("/results/{img}")
async def get_image(img: str):
  client = storage.Client()
  bucket_name = "lila-ai-demo-api-server"
  bucket = client.get_bucket(bucket_name)
  blob = bucket.blob(img)
  image_bytes = blob.download_as_bytes()

  return Response(content=image_bytes, media_type="image/png")  
