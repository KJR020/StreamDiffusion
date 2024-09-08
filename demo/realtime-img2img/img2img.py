import sys
import os

sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
    )
)

from utils.wrapper import StreamDiffusionWrapper

import torch

from config import Args
from pydantic import BaseModel, Field
from PIL import Image

# base_model = "stabilityai/sd-turbo"
# base_model = "KBlueLeaf/kohaku-v2.1"
base_model = r"D:\work\StreamDiffusion\models\Model\dreamshaper_8.safetensors"
taesd_model = "madebyollin/taesd"

# default_prompt = "1girl with brown dog ears, thick frame glasses"
default_prompt = """
cgmech, (realistic) solo, white mecha robot, cape, science fiction, torn clothes, glowing, standing, robot joints, mecha, armor, cowboy shot, (floating cape), intense sunlight, silver dragonborn, outdoors, landscape, nature , ((masterpiece, best quality)), <lora:cgmechmix_offset:1><lora:more_details:0.3> <lora:Niji:0.5><lora:dragonborn_offset:0.7> , volumetrics dtx, (film grain, blurry background, blurry foreground, bokeh, depth of field, motion blur:1.3)
"""

default_negative_prompt = "black and white, blurry, low resolution, pixelated,  pixel art, low quality, low fidelity"

page_content = """<h1 class="text-3xl font-bold">StreamDiffusion</h1>
<h3 class="text-xl font-bold">Image-to-Image SD-Turbo</h3>
<p class="text-sm">
    This demo showcases
    <a
    href="https://github.com/cumulo-autumn/StreamDiffusion"
    target="_blank"
    class="text-blue-500 underline hover:no-underline">StreamDiffusion
</a>
Image to Image pipeline using
    <a
    href="https://huggingface.co/stabilityai/sd-turbo"
    target="_blank"
    class="text-blue-500 underline hover:no-underline">SD-Turbo</a
    > with a MJPEG stream server.
</p>
"""


class Pipeline:
    class Info(BaseModel):
        name: str = "StreamDiffusion img2img"
        input_mode: str = "image"
        page_content: str = page_content

    class InputParams(BaseModel):
        prompt: str = Field(
            default_prompt,
            title="Prompt",
            field="textarea",
            id="prompt",
        )
        # negative_prompt: str = Field(
        #     default_negative_prompt,
        #     title="Negative Prompt",
        #     field="textarea",
        #     id="negative_prompt",
        # )
        width: int = Field(512, min=2, max=15, title="Width", disabled=True, hide=True, id="width")
        height: int = Field(512, min=2, max=15, title="Height", disabled=True, hide=True, id="height")

    def __init__(self, args: Args, device: torch.device, torch_dtype: torch.dtype):
        params = self.InputParams()
        self.stream = StreamDiffusionWrapper(
            model_id_or_path=base_model,
            use_tiny_vae=args.taesd,
            device=device,
            dtype=torch_dtype,
            t_index_list=[35, 45],
            frame_buffer_size=1,
            width=params.width,
            height=params.height,
            use_lcm_lora=False,
            output_type="pil",
            warmup=10,
            vae_id=None,
            acceleration=args.acceleration,
            mode="img2img",
            use_denoising_batch=True,
            cfg_type="none",
            use_safety_checker=args.safety_checker,
            enable_similar_image_filter=True,
            similar_image_filter_threshold=0.98,
            engine_dir=args.engine_dir,
        )

        self.last_prompt = default_prompt
        self.stream.prepare(
            prompt=default_prompt,
            negative_prompt=default_negative_prompt,
            num_inference_steps=50,
            guidance_scale=1.2,
        )

    def predict(self, params: "Pipeline.InputParams") -> Image.Image:
        image_tensor = self.stream.preprocess_image(params.image)
        output_image = self.stream(image=image_tensor, prompt=params.prompt)

        return output_image
