import asyncio
from azure.identity.aio import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient
import os
import glob

current_file_directory = os.path.dirname(os.path.abspath(__file__))
apples_path = os.path.join(current_file_directory, "..", "..", "..", "data", "images", "apples")
async def main():
    credential = DefaultAzureCredential()
    blob_client = BlobServiceClient(account_url=os.getenv("AZURE_STORAGE_ACCOUNT_BLOB_URL"), credential=credential)
    await upload_images(blob_client)

async def upload_images(blob_client: BlobServiceClient):
    container_client = blob_client.get_container_client(os.getenv("AZURE_STORAGE_CONTAINER"))
    image_paths = glob.glob(os.path.join(apples_path, "*.jpeg"))
    for image_path in image_paths:
        with open(image_path, "rb") as data:
            await container_client.upload_blob(name=os.path.basename(image_path), data=data)

if __name__ == "__main__":
    asyncio.run(main())