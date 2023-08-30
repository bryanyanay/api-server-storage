FROM python:3.11

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install torch torchvision
RUN pip install mmengine
RUN pip install -U openmim
RUN mim install "mmcv>=2.0.0rc2"
RUN pip install mmdeploy
RUN pip install onnxruntime


RUN git clone -b main https://github.com/open-mmlab/mmdeploy.git

COPY mmsegmentation /app/mmsegmentation
WORKDIR /app/mmsegmentation
RUN pip install -v -e .

WORKDIR /app
RUN pip install fastapi uvicorn aiofiles python-multipart
RUN pip install google-cloud-storage

# RUN mkdir static
RUN mkdir images

# COPY dynamic_dir /app/dynamic_dir
COPY main.py /app/main.py
COPY segformer.pth /app/segformer.pth
COPY PSPNet.pth /app/PSPNet.pth

RUN apt-get update && apt-get -y install libgl1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]





