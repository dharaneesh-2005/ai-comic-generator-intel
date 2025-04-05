import io
import warnings
import random
from PIL import Image
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
import streamlit as st

# Get Stability AI key from secrets
api_key = st.secrets["stability"]["api_key"]

seed = random.randint(0, 1000000000)

stability_api = client.StabilityInference(
    key=api_key,
    verbose=True,
    engine="stable-diffusion-xl-1024-v1-0",
)

def text_to_image(prompt):
    answers = stability_api.generate(
        prompt=prompt,
        seed=seed, 
        steps=30, 
        cfg_scale=8.0, 
        width=1024,  
        height=1024, 
        sampler=generation.SAMPLER_K_DPMPP_2M  
    )
    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                warnings.warn(
                    "Your request activated the API's safety filters and could not be processed."
                    "Please modify the prompt and try again."
                )
            if artifact.type == generation.ARTIFACT_IMAGE:
                global img
                img = Image.open(io.BytesIO(artifact.binary))
                return img


def edit_image(input_image_path, prompt, output_image_name):
    img = Image.open(input_image_path)

    answers = stability_api.generate(
        prompt=prompt,
        init_image=img,  
        start_schedule=0.6, 
        seed=123463446,  
        steps=50,  
        cfg_scale=8.0,  
        width=512,  
        height=512, 
        sampler=generation.SAMPLER_K_DPMPP_2M  
    )

    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                warnings.warn(
                    "Your request activated the API's safety filters and could not be processed."
                    "Please modify the prompt and try again."
                )
            if artifact.type == generation.ARTIFACT_IMAGE:
                global img2
                img2 = Image.open(io.BytesIO(artifact.binary))
                img2.save(
                    output_image_name + ".png"
                )  

