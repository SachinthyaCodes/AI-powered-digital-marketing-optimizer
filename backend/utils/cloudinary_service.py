import cloudinary
import cloudinary.uploader
from config import Config

# Configure Cloudinary
cloudinary.config(
    cloud_name=Config.CLOUDINARY_CLOUD_NAME,
    api_key=Config.CLOUDINARY_API_KEY,
    api_secret=Config.CLOUDINARY_API_SECRET
)

class CloudinaryService:
    @staticmethod
    def upload_image(file, folder="marketmatic"):
        """
        Upload image to Cloudinary
        Returns: dict with url and public_id
        """
        try:
            result = cloudinary.uploader.upload(
                file,
                folder=folder,
                transformation=[
                    {'width': 1000, 'height': 1000, 'crop': 'limit'},
                    {'quality': 'auto'}
                ]
            )
            return {
                'url': result['secure_url'],
                'public_id': result['public_id']
            }
        except Exception as e:
            print(f"Error uploading to Cloudinary: {str(e)}")
            return None
    
    @staticmethod
    def upload_file(file_content, public_id, folder="marketmatic", resource_type="auto"):
        """
        Upload file (document/image) to Cloudinary
        Returns: dict with url and public_id
        """
        try:
            result = cloudinary.uploader.upload(
                file_content,
                folder=folder,
                public_id=public_id,
                resource_type=resource_type
            )
            return {
                'url': result['secure_url'],
                'public_id': result['public_id'],
                'resource_type': result['resource_type'],
                'format': result.get('format'),
                'bytes': result.get('bytes')
            }
        except Exception as e:
            print(f"Error uploading file to Cloudinary: {str(e)}")
            return None
    
    @staticmethod
    def delete_image(public_id):
        """Delete image from Cloudinary"""
        try:
            cloudinary.uploader.destroy(public_id)
            return True
        except Exception as e:
            print(f"Error deleting from Cloudinary: {str(e)}")
            return False
    
    @staticmethod
    def upload_multiple_images(files, folder="marketmatic"):
        """Upload multiple images to Cloudinary"""
        results = []
        for file in files:
            result = CloudinaryService.upload_image(file, folder)
            if result:
                results.append(result)
        return results
