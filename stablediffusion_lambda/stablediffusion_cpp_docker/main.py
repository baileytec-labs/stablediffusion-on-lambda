import os
import json
import traceback
import subprocess
import time
import uuid
import httpx
import boto3
import random
import re
from PIL import Image
import xbrz

from fastapi import FastAPI, Header, HTTPException, Request, Form, UploadFile, File
from mangum import Mangum
from botocore.exceptions import NoCredentialsError

# Environment Variables
IMAGE_DIMENSION = int(os.environ.get("IMAGE_DIMENSION"))
MODELPATH = os.environ.get("MODELPATH")
SDPATH = os.environ.get("SDPATH")
BUCKET_NAME = os.environ.get("BUCKET_NAME")
stage = os.environ.get('STAGE', None)
openapi_prefix = f"/{stage}" if stage else "/"

app = FastAPI(title="Stable Diffusion on Lambda API", root_path=openapi_prefix)
print("Lambda Function Loaded")


def upscale_image(input_path, output_path, scale_factor):
    # Load the image using Pillow
    input_image = Image.open(input_path)
    
    # Convert the image to RGBA (if it's not already in that mode)
    input_image_rgba = input_image.convert('RGBA')
    
    # Upscale the image using xbrz.scale_pillow
    upscaled_image = xbrz.scale_pillow(input_image_rgba, scale_factor)
    
    # Save the upscaled image
    upscaled_image.save(output_path)

def download_from_s3(objectname: str) -> str:
    print("Download from s3")
    s3 = boto3.client('s3')
    local_path = f"/tmp/{objectname.split('/')[-1]}"
    s3.download_file(BUCKET_NAME, objectname, local_path)
    return local_path


def shuffle_string(s: str) -> str:
    print("Shuffle String")
    char_list = list(s)
    random.shuffle(char_list)
    return ''.join(char_list)


def execute_and_upload(cmd, output,scale):
    # Create the subprocess
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True)

    # Continuously read from stdout
    while True:
        # Read one line from stdout
        line = process.stdout.readline()
        if not line:
            break  # Exit the loop when there is nothing left to read
        print(line, end='')  # Print the line (end='' prevents adding an extra newline)

    # Wait for the subprocess to finish
    process.communicate()  # This will also read any remaining output
    return_code = process.returncode

    # Check the return code
    if return_code != 0:
        # Get any error output
        error_output = process.stderr.read()
        raise HTTPException(status_code=500, detail=error_output)
    upscale_image(output,output,scale)
    # Upload the output
    return upload_output(output)



@app.post("/execute")
def execute_binary(
    mode: str = Form("txt2img", description="Generation mode (txt2img or img2img)"),
    threads: int = Form(-1, description="Number of threads to use during computation"),
    model: str = Form(MODELPATH, description="Path to model"),
    init_img: str = Form(None, description="S3 location of the input image, required by img2img"),
    prompt: str = Form(..., description="The prompt to render"),
    negative_prompt: str = Form("", description="The negative prompt"),
    cfg_scale: float = Form(7.0, description="Unconditional guidance scale"),
    strength: float = Form(0.75, description="Strength for noising/unnoising"),
    #height: int = Form(128, description="Image height, in pixel space"),
    #width: int = Form(128, description="Image width, in pixel space"),
    scale: int = Form(4, description="How large you wish to scale the image, default 4x"),
    sampling_method: str = Form("euler_a", description="Sampling method"),
    steps: int = Form(10, description="Number of sample steps"),
    rng: str = Form("cuda", description="RNG"),
    seed: int = Form(-1, description="RNG seed"),
    schedule: str = Form("discrete", description="Denoiser sigma schedule"),
    verbose: bool = Form(False, description="Print extra info")
    ):
    height = IMAGE_DIMENSION
    width = IMAGE_DIMENSION
    print("execute binary")
    output="/tmp/"+shuffle_string(str(uuid.uuid4()).split("-")[-1]+str(time.time()).replace(".",""))+".png"
    print("Now generating command")
    # Construct the command
    cmd = [
        SDPATH,
        "--mode", mode,
        "--threads", str(threads),
        "--model", model,
        "--output", output,
        "--prompt", prompt,
        "--negative-prompt", negative_prompt,
        "--cfg-scale", str(cfg_scale),
        "--strength", str(strength),
        "--height", str(height),
        "--width", str(width),
        "--sampling-method", sampling_method,
        "--steps", str(steps),
        "--rng", rng,
        "--seed", str(seed),
        "--schedule", schedule,
    ]
    
    if verbose:
        cmd.append("--verbose")
    if init_img:
        cmd.extend(["--init-img", download_from_s3(init_img)])
    print(cmd)
    try:
        return execute_and_upload(cmd, output,scale)
    except Exception as e:
        print(e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


def upload_output(file_path: str) -> dict:
    print("Upload output")
    s3 = boto3.client('s3')
    file_name = file_path.split("/")[-1]
    s3.upload_file(file_path, BUCKET_NAME, file_name)
    presigned_url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': BUCKET_NAME, 'Key': file_name},
        ExpiresIn=3600
    )
    print(presigned_url)
    return {"presigned_url": presigned_url}



@app.post("/upload")
async def upload_file_to_s3(file: UploadFile = File(...)):
    print("Upload file to s3")
    s3 = boto3.client('s3')
    unique_filename = shuffle_string(str(uuid.uuid4()).replace("-", "") + str(time.time()).replace(".", ""))
    unique_filename += "." + file.filename.split(".")[-1]
    file_content = await file.read()
    s3.put_object(Body=file_content, Bucket=BUCKET_NAME, Key=unique_filename)
    return {"unique_filename": unique_filename}

@app.get("/healthcheck")
def healthcheck():
    print("Healthcheck")
    return {"status": "OK"}

handler=Mangum(app)


