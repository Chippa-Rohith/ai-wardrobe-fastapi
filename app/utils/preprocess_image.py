from rembg import remove
from PIL import Image
import numpy as np
import io
import os
from azure.storage.blob import BlobServiceClient
import uuid
import pillow_heif
from dotenv import load_dotenv

load_dotenv()

IMAGE_SIZE = [80, 60]

# Load Azure Blob Storage configuration from environment variables
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_STORAGE_CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

# Initialize BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)


def upload_to_blob(image_data, file_extension):
    """Uploads the processed image to Azure Blob Storage."""
    try:
        # Generate a unique filename
        unique_filename = f"{uuid.uuid4()}{file_extension}"

        # Get a BlobClient for the file
        blob_client = blob_service_client.get_blob_client(container=AZURE_STORAGE_CONTAINER_NAME, blob=unique_filename)

        # Upload the file
        blob_client.upload_blob(image_data, overwrite=True)

        # Generate and return the file URL
        file_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{AZURE_STORAGE_CONTAINER_NAME}/{unique_filename}"
        return file_url
    except Exception as e:
        raise Exception(f"Failed to upload to Azure Blob Storage: {str(e)}")


def preprocess_image(image_bytes, file_extension=".png"):
    """Preprocess the image: remove background, upload to Azure Blob Storage, resize, and prepare for model."""
    try:
        # Handle HEIC files
        if file_extension and file_extension.lower() == ".heic":
            heif_file = pillow_heif.read_heif(io.BytesIO(image_bytes))
            image = Image.frombytes(heif_file.mode, heif_file.size, heif_file.data, "raw")
        else:
            # For other formats (PNG, JPG, etc.)
            image = Image.open(io.BytesIO(image_bytes))

        # Remove background
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        input_image = buffer.getvalue()
        output_image = remove(input_image)
        image = Image.open(io.BytesIO(output_image))

        # Add a white background
        white_bg = Image.new("RGBA", image.size, (255, 255, 255, 255))
        final_image = Image.alpha_composite(white_bg, image.convert("RGBA"))

        # Convert to RGB
        final_image = final_image.convert("RGB")

        # Save the processed full-resolution image to a binary stream
        full_res_buffer = io.BytesIO()
        final_image.save(full_res_buffer, format="JPEG")
        full_res_image_bytes = full_res_buffer.getvalue()

        # Upload the full-resolution processed image to Azure Blob Storage
        image_url = upload_to_blob(full_res_image_bytes, file_extension=".jpeg")

        # Resize the image for model input
        resized_image = final_image.resize((IMAGE_SIZE[1], IMAGE_SIZE[0]))

        # Convert the resized image to a NumPy array for model input
        image_array = np.array(resized_image)

        return image_url, image_array
    except Exception as e:
        raise Exception(f"Error processing image: {e}")