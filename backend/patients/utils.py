import cloudinary.uploader
import uuid
import logging
logger = logging.getLogger(__name__)

def upload_patient_image(image_file, tenant_schema):
    """
    Upload patient profile picture to Cloudinary
    """
    try:
        # Generate a unique image name
        image_name = f"patient_profile_{tenant_schema}_{uuid.uuid4().hex[:8]}"
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            image_file,
            folder="patient_profiles",  # Organize images in folders
            public_id=image_name,
            resource_type="auto",
            
            # This is optional
            transformation=[
                {'width': 800, 'height': 800, 'crop': 'limit'},  # Resize if too large
                {'quality': 'auto:good'}  # Automatic quality optimization
            ]
        )
        
        return result.get("secure_url")
    except Exception as e:
        # Log the error
        logger.error(f"Cloudinary upload failed: {str(e)}")
        raise ValueError("Image upload failed")