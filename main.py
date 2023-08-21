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
      <!--select name=model>
        <option value=pspnet>PSPnet</option>
        <option value=segformer>Segformer</option>
      </select-->
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
  
  client = storage.Client()
  bucket = client.get_bucket("lila-ai-demo-api-server")
  blob = bucket.blob(args.out_file)
  blob.upload_from_filename("./" + args.out_file)

  return args.out_file


def segmentImgPSPNET(curr):
  deploy_cfg = './mmdeploy/configs/mmseg/segmentation_onnxruntime_dynamic.py'
  model_cfg = './mmsegmentation/configs/pspnet/pspnet_r50-d8_80k_foodwaste.py'
  device = 'cpu'
  backend_model = ['./dynamic_dir/onnx/pspnet/end2end.onnx']
  image = f"images/input_M{curr}.png"

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

  return outputImg

@app.post("/segment/")
async def handle_post_segment(image: UploadFile, model: str = Form("pspnet")):
  curr = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")

  print(model)

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

  return {"status": "OK",
          "resultPath": f"/results/{outFile}"}

@app.get("/results/{img}")
async def get_image(img: str):
  client = storage.Client()
  bucket_name = "lila-ai-demo-api-server"
  bucket = client.get_bucket(bucket_name)
  blob = bucket.blob(img)
  image_bytes = blob.download_as_bytes()

  return Response(content=image_bytes, media_type="image/png")  

