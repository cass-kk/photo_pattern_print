import os
import image_pull
import pattern_gen
from PIL import Image

def get_next_file_name(base_name="final_pattern_tile", extension=".png"):
    # Finds the next available filename by checking existing files
    # If 'final_pattern_tile1.png' exists, it moves to 'final_pattern_tile2.png', etc

    counter = 1
    while os.path.exists(f"{base_name}{counter}{extension}"):
        counter += 1
    return f"{base_name}{counter}{extension}"

def get_most_recent_folder(base_name="flower_edited"):
    # Scans the current directory to locate the folder with the highest index number.
    # e.g., if 'flower_edited1', 'flower_edited2', and 'flower_edited3' exist, it returns 'flower_edited3'

    counter = 1
    highest_found = None
    while os.path.exists(f"{base_name}{counter}"):
        highest_found = f"{base_name}{counter}"
        counter += 1
    return highest_found

def run_fabric_pipeline():
    print("        STARTING FABRIC PATTERN PIPELINE          ")
    
    # User Menu Prompt
    print("Select an option:")
    print(" [1] Extract flowers from 'flowers_raw' and generate a new pattern")
    print(" [2] Skip extraction (Use files from your most recent edited folder)")
    user_choice = input("Enter choice (1 or 2): ").strip()
    
    generated_folder = None
    
    if user_choice == "1":
        # Step 1: Standard full pipeline extraction
        generated_folder = image_pull.process_raw_folder(
            input_folder="flowers_raw", 
            output_folder="flower_edited", 
            bridge_gap=15 
        )
    elif user_choice == "2":
        # Step 1 Bypassed: Dynamically fetch your last used edited folder
        generated_folder = get_most_recent_folder("flower_edited")
        if generated_folder:
            print(f"\n[main] Skipping extraction. Bypassing directly to folder: '{generated_folder}/'")
        else:
            # Fallback check if you haven't ever run an automated extraction yet
            print("\nNo auto-generated folder found! Checking for standard 'flower_edited' directory...")
            if os.path.exists("flower_edited"):
                generated_folder = "flower_edited"
    else:
        print("Invalid input selection. Exiting pipeline script.")
        return
    
    # Master directory validation boundary check
    if not generated_folder or not os.path.exists(generated_folder) or len(os.listdir(generated_folder)) == 0:
        print(f"Pipeline stopped: The directory target is empty or invalid.")
        return

    # Dynamic File Versioning
    output_pattern_file = get_next_file_name(base_name="final_pattern_tile", extension=".png")
    print(f"[main] Target output filename locked: {output_pattern_file}")

    # Step 2: Formulate pattern from our directory
    pattern_gen.generate_seamless_pattern(
        input_folder=generated_folder, 
        output_path=output_pattern_file,
        sub_tile_size=2000, 
        total_objs=50       
    )
    
    # Step 3: View the final master pattern asset
    if os.path.exists(output_pattern_file):
        print(f"\nOpening generated canvas file ({output_pattern_file}) for preview...")
        img = Image.open(output_pattern_file)
        img.show()

if __name__ == "__main__":
    run_fabric_pipeline()
