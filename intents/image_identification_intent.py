from PIL import Image
from langchain.tools import BaseTool
import requests
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration


class ImageCaptionTool(BaseTool):
    name = "Image_captioner"
    description = "Use this tool when given the URL of an image that you'd like to be described. It will return a simple caption describing the image."
    
    def _run(self, url: str) -> str:
        # use GPU if it's available
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # load processor and model from path -> first time needs to be downloaded
        processor = BlipProcessor.from_pretrained("./image_model")
        model = BlipForConditionalGeneration.from_pretrained("./image_model").to(device)

        # # load image from path
        # image_file_path = 'image_file_name.jpg'

        # # Load the image from the current folder
        # image = Image.open(image_file_path)

        # download the image and convert to PIL object
        image = Image.open(requests.get(url, stream=True).raw).convert('RGB')

        # preprocess the image
        inputs = processor(image, return_tensors="pt").to(device)

        # generate the caption
        out = model.generate(**inputs, max_new_tokens=20)

        # get the caption
        caption = processor.decode(out[0], skip_special_tokens=True)
        return caption + "\n"
    
    def _arun(self, url: str) -> str:
        raise NotImplementedError("This tool does not support async")

def download_and_save_model(path):
    # specify model to be used
    hf_model = "Salesforce/blip-image-captioning-large"
    # use GPU if it's available
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    # preprocessor will prepare images for the model
    processor = BlipProcessor.from_pretrained(hf_model)
    processor.save_pretrained(path)
    # then we initialize the model itself
    model = BlipForConditionalGeneration.from_pretrained(hf_model).to(device)
    model.save_pretrained(path)

def describe_image(img_url = None, path = None):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    processor = BlipProcessor.from_pretrained("./image_model")
    model = BlipForConditionalGeneration.from_pretrained("./image_model").to(device)
    if img_url:
        image = Image.open(requests.get(img_url, stream=True).raw).convert('RGB')
    elif path:
        image = Image.open(path)
    else:
        print("No input provided!")
    # unconditional image captioning
    inputs = processor(image, return_tensors="pt").to(device)

    out = model.generate(**inputs, max_new_tokens=20)
    print(processor.decode(out[0], skip_special_tokens=True))

if __name__ == "__main__":
    img_url = 'https://images.unsplash.com/photo-1616128417859-3a984dd35f02?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2372&q=80' 
    path = "./pictures/drawer3.jpg"
    describe_image(path=path)