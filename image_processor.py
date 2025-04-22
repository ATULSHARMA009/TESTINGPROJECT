import cv2
import numpy as np
from PIL import Image
from rembg import remove
from skimage import restoration, transform
import os
from tqdm import tqdm

class ImageProcessor:
    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    
    def remove_background(self, image_path, output_path):
        """Remove background from an image while preserving the main subject."""
        try:
            # Ensure output path ends with .png
            output_path = os.path.splitext(output_path)[0] + '.png'
            
            input_image = Image.open(image_path)
            output_image = remove(input_image)
            output_image.save(output_path, 'PNG')  # Explicitly save as PNG
            print(f"Successfully saved output to: {output_path}")
            return True
        except Exception as e:
            print(f"Error removing background: {str(e)}")
            return False

    def enhance_quality(self, image_path, output_path):
        """Enhance image quality by reducing noise and improving sharpness."""
        try:
            img = cv2.imread(image_path)
            # Denoise the image
            denoised = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
            # Sharpen the image
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            sharpened = cv2.filter2D(denoised, -1, kernel)
            cv2.imwrite(output_path, sharpened)
            return True
        except Exception as e:
            print(f"Error enhancing image: {str(e)}")
            return False

    def resize_without_distortion(self, image_path, output_path, new_width=None, new_height=None):
        """Resize image while maintaining aspect ratio and preventing distortion."""
        try:
            img = Image.open(image_path)
            if new_width and new_height:
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            elif new_width:
                ratio = new_width / float(img.size[0])
                new_height = int(float(img.size[1]) * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            elif new_height:
                ratio = new_height / float(img.size[1])
                new_width = int(float(img.size[0]) * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            img.save(output_path)
            return True
        except Exception as e:
            print(f"Error resizing image: {str(e)}")
            return False

    def remove_unwanted_objects(self, image_path, output_path, mask_path=None):
        """Remove unwanted objects from an image using inpainting."""
        try:
            img = cv2.imread(image_path)
            if mask_path:
                mask = cv2.imread(mask_path, 0)
            else:
                # Create a simple mask for demonstration
                mask = np.zeros(img.shape[:2], dtype=np.uint8)
                # Example: remove a rectangular area
                mask[100:200, 100:200] = 255
            
            result = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)
            cv2.imwrite(output_path, result)
            return True
        except Exception as e:
            print(f"Error removing objects: {str(e)}")
            return False

    def fix_perspective(self, image_path, output_path, corners):
        """Fix perspective distortion in images."""
        try:
            img = cv2.imread(image_path)
            # Convert corners to numpy array
            pts = np.array(corners, dtype=np.float32)
            # Define the target rectangle
            width = max(np.linalg.norm(pts[0] - pts[1]), np.linalg.norm(pts[2] - pts[3]))
            height = max(np.linalg.norm(pts[0] - pts[3]), np.linalg.norm(pts[1] - pts[2]))
            target = np.array([[0, 0], [width, 0], [width, height], [0, height]], dtype=np.float32)
            
            # Calculate perspective transform
            matrix = cv2.getPerspectiveTransform(pts, target)
            result = cv2.warpPerspective(img, matrix, (int(width), int(height)))
            cv2.imwrite(output_path, result)
            return True
        except Exception as e:
            print(f"Error fixing perspective: {str(e)}")
            return False

    def batch_process(self, input_dir, output_dir, process_type, **kwargs):
        """Process multiple images in a directory."""
        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            files = [f for f in os.listdir(input_dir) if any(f.lower().endswith(ext) for ext in self.supported_formats)]
            
            for file in tqdm(files, desc=f"Processing {process_type}"):
                input_path = os.path.join(input_dir, file)
                
                # Handle PNG output for background removal
                if process_type == "remove_background":
                    output_name = os.path.splitext(file)[0] + ".png"
                else:
                    output_name = file
                    
                output_path = os.path.join(output_dir, output_name)
                
                if process_type == "remove_background":
                    self.remove_background(input_path, output_path)
                elif process_type == "enhance_quality":
                    self.enhance_quality(input_path, output_path)
                elif process_type == "resize":
                    self.resize_without_distortion(input_path, output_path, **kwargs)
                elif process_type == "remove_objects":
                    self.remove_unwanted_objects(input_path, output_path, **kwargs)
                elif process_type == "fix_perspective":
                    self.fix_perspective(input_path, output_path, **kwargs)
            
            return True
        except Exception as e:
            print(f"Error in batch processing: {str(e)}")
            return False 