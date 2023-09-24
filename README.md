# Stable Diffusion Models running on AWS Lambda

:warning: **FOR EDUCATIONAL PURPOSES ONLY** :warning:

Docker images, code, buildspecs, and guidance provided as proof of concept only and for educational purposes only.

This repository demonstrates a proof of concept (PoC) of running Stable Diffusion Models on AWS Lambda, showcasing the potential of serverless architecture in handling text-to-image and image-to-image generative AI tasks. This PoC is primarily educational and experimental, aiming to bridge the gap between theory and practical implementation.

## 🚀 Quick Overview
Utilizing the quantization advancements from the [GGML Project](https://github.com/ggerganov/ggml) and the ported diffusion models in [stable-diffusion.cpp](https://github.com/leejet/stable-diffusion.cpp), this PoC enables the deployment of generative AI models on AWS Lambda. By employing models optimized for 256x256 or 128x128 image generation like [MiniSD](https://huggingface.co/justinpinkney/miniSD/tree/main) and [stable-diffusion-nano](https://huggingface.co/bguisard/stable-diffusion-nano-2-1/tree/main), we significantly reduce image generation time and computational resources. The [XBRZ](https://github.com/ioistired/xbrz.py) library further allows efficient image upscaling up to 7x, making this serverless setup a scalable solution for image generation tasks.

## 🛠 Prerequisites
Before diving in, ensure you have:
- Python 3.10+ and pip
- AWS CDK
- Docker
- An AWS account with necessary credentials



## 🚀 Deployment
1. Clone this repository.
2. Navigate to the `stablediffusion_lambda` folder:
   ```bash
   cd stablediffusion-on-lambda/stablediffusion_lambda
   ``````

# Deployment

1) Clone this repository
2) CD into this repository and then into the stablediffusion_lambda folder

```bash

cd stablediffusion-on-lambda/stablediffusion_lambda

```

3) Set up a virtual environment, activate it, and install dependencies:

```bash

python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt


```

4) Deploy the architecture

```bash

cdk deploy


```

Upon successful deployment, you'll receive a URL to your FastAPI endpoint documentation, where you can interact with the deployed model.

# 📚 Usage

Interact with your endpoint using the provided Lambda Function URL.  If you'd like to use a different model, go to the `dockerfile` in the `stablediffusion_cpp_docker` folder and modify the `FOUNDATIONMODEL` to your model url, and `IMAGE_DIMENSION` to match the default image dimension of the model you're using. This repo recommends 128x128 or 256x256 models, as 512x512 models and up take significant time and may have to tweak the steps value to fit within the 15 minute runtime of the Lambda function.


## Endpoints

### POST `/execute`

Generates an image based on the provided parameters.

#### Parameters:

- `mode` (str, default: "txt2img"): Generation mode (`txt2img` or `img2img`).
- `threads` (int, default: -1): Number of threads to use during computation.
- `model` (str, default: `MODELPATH`): Path to model.
- `init_img` (str, optional): S3 location of the input image, required by `img2img`.
- `prompt` (str): The prompt to render.
- `negative_prompt` (str, default: ""): The negative prompt.
- `cfg_scale` (float, default: 7.0): Unconditional guidance scale.
- `strength` (float, default: 0.75): Strength for noising/unnoising.
- `scale` (int, default: 4): How large you wish to scale the image, default 4x.
- `sampling_method` (str, default: "euler_a"): Sampling method.
- `steps` (int, default: 10): Number of sample steps.
- `rng` (str, default: "cuda"): RNG.
- `seed` (int, default: -1): RNG seed.
- `schedule` (str, default: "discrete"): Denoiser sigma schedule.
- `verbose` (bool, default: False): Print extra info.

#### Example Request:

```bash
curl -X POST "https://your-api-url/execute" \
     -d "mode=txt2img&prompt=Your Prompt Here"

```

### POST /upload
Uploads a file to the specified S3 bucket.

Parameters:
file (file): The file to be uploaded.
Example Request:

```
curl -X POST "https://your-api-url/upload" \
     -F "file=@your-file.jpg"


```


### GET /healthcheck
Checks the health of the API.

Example Request:

```
curl "https://your-api-url/healthcheck"


```

### Response
The /execute endpoint returns a presigned URL to the generated image in the S3 bucket:

```
{
    "presigned_url": "https://your-s3-bucket.s3.amazonaws.com/generated-image.png?AWSAccessKeyId=..."
}


```

The /upload endpoint returns the unique filename of the uploaded file in the S3 bucket:

```
{
    "unique_filename": "unique-filename.jpg"
}


```

The /healthcheck endpoint returns a status indicating the health of the API:

```
{
    "status": "OK"
}


```


# 📝 Notes
This project is under the Apache 2 license. Please check the licenses for XBRZ and any models you use. Contributions are welcome; see CONTRIBUTION.md for details.



# <a name="connect"></a> 🤝 Connect & Support

<a href="https://www.baileytec.net" target="_blank"><img alt="Website" src="https://img.shields.io/badge/Personal%20Website-%2312100E.svg?&style=for-the-badge&logoColor=white" /></a>
<a href="https://medium.com/@seanbailey518" target="_blank"><img alt="Medium" src="https://img.shields.io/badge/medium-%2312100E.svg?&style=for-the-badge&logo=medium&logoColor=white" /></a>
<a href="https://www.linkedin.com/in/baileytec/" target="_blank"><img alt="LinkedIn" src="https://img.shields.io/badge/linkedin-%230077B5.svg?&style=for-the-badge&logo=linkedin&logoColor=white" /></a><a href="https://www.buymeacoffee.com/baileyteclabs" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-blue.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>