from image_processor import ImageProcessor
import os

def main():
    # Create an instance of ImageProcessor
    processor = ImageProcessor()
    
    # Create input and output directories
    input_dir = "input_images"
    output_dir = "output_images"
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    print("Image Processing System - Common Daily Issues Solver")
    print("===================================================")
    print("1. Remove background from images")
    print("2. Enhance image quality")
    print("3. Resize images without distortion")
    print("4. Remove unwanted objects")
    print("5. Fix perspective distortion")
    print("6. Batch process multiple images")
    
    choice = input("\nEnter your choice (1-6): ")
    
    if choice == "1":
        # Remove background
        image_path = input("Enter image path: ")
        # Output will always be PNG for background removal
        output_name = "no_bg_" + os.path.splitext(os.path.basename(image_path))[0] + ".png"
        output_path = os.path.join(output_dir, output_name)
        if processor.remove_background(image_path, output_path):
            print(f"Background removed. Output saved to: {output_path}")
        else:
            print("Failed to remove background. Please check the error message above.")
    
    elif choice == "2":
        # Enhance quality
        image_path = input("Enter image path: ")
        output_path = os.path.join(output_dir, "enhanced_" + os.path.basename(image_path))
        processor.enhance_quality(image_path, output_path)
        print(f"Image enhanced. Output saved to: {output_path}")
    
    elif choice == "3":
        # Resize image
        image_path = input("Enter image path: ")
        width = int(input("Enter new width (or 0 to maintain aspect ratio): "))
        height = int(input("Enter new height (or 0 to maintain aspect ratio): "))
        output_path = os.path.join(output_dir, "resized_" + os.path.basename(image_path))
        processor.resize_without_distortion(image_path, output_path, 
                                          new_width=width if width > 0 else None,
                                          new_height=height if height > 0 else None)
        print(f"Image resized. Output saved to: {output_path}")
    
    elif choice == "4":
        # Remove objects
        image_path = input("Enter image path: ")
        mask_path = input("Enter mask path (or press Enter to use default): ")
        output_path = os.path.join(output_dir, "cleaned_" + os.path.basename(image_path))
        processor.remove_unwanted_objects(image_path, output_path, 
                                       mask_path=mask_path if mask_path else None)
        print(f"Objects removed. Output saved to: {output_path}")
    
    elif choice == "5":
        # Fix perspective
        image_path = input("Enter image path: ")
        print("Enter four corner points (x,y) for perspective correction:")
        corners = []
        for i in range(4):
            x = float(input(f"Point {i+1} x: "))
            y = float(input(f"Point {i+1} y: "))
            corners.append([x, y])
        output_path = os.path.join(output_dir, "corrected_" + os.path.basename(image_path))
        processor.fix_perspective(image_path, output_path, corners)
        print(f"Perspective corrected. Output saved to: {output_path}")
    
    elif choice == "6":
        # Batch process
        print("\nAvailable process types:")
        print("1. remove_background (outputs will be PNG)")
        print("2. enhance_quality")
        print("3. resize")
        print("4. remove_objects")
        print("5. fix_perspective")
        process_type = input("\nEnter process type: ")
        
        # Map numeric input to process type
        process_map = {
            "1": "remove_background",
            "2": "enhance_quality",
            "3": "resize",
            "4": "remove_objects",
            "5": "fix_perspective"
        }
        
        if process_type in process_map:
            process_type = process_map[process_type]
            processor.batch_process(input_dir, output_dir, process_type)
            print(f"Batch processing complete. Output saved to: {output_dir}")
        else:
            print("Invalid process type!")
    
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    main() 