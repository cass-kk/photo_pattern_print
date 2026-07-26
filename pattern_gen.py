import os
import random
import numpy as np
from PIL import Image
import config

def get_distance(p1, p2):
    # Calculates standard Euclidean distance between two center points
    return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5

def generate_seamless_pattern(input_folder=config.edited_photos, output_path=config.generated_pattern_path, sub_tile_size=1200, total_objs=80):
    # Assembles a completely random fabric pattern panel across a massive master canvas.
    # Uses toroidal boundary calculations to maintain a perfect spacing buffer without mirror lines.
    
    flower_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.lower().endswith('.png')]
    
    if not flower_files:
        print(f"[pattern_gen] Error: No flower objects found in '{input_folder}/'.")
        return None

    # Define the absolute size of the final output print panel (Mirroring the 2x2 size)
    master_size = sub_tile_size * 2
    master_canvas = Image.new("RGBA", (master_size, master_size), (245, 245, 245, 255))
    
    # Track placed flower configurations: (center_x, center_y, protective_radius)
    placed_flowers = []
    
    # ADJUST THIS VALUE TO CONTROL THE WHITE SPACE GAP
    # This is the minimum separation distance (in pixels) required between flower edges.
    # Increase this (e.g., 40) for wider gaps. Decrease it (e.g., 10) to pack them tight.
    edge_separation_buffer = config.white_space_gap

    print(f"[pattern_gen] Distributing {total_objs} assets randomly across a {master_size}x{master_size} canvas...")

    for i in range(total_objs):
        chosen_flower_path = random.choice(flower_files)
        source_flower = Image.open(chosen_flower_path).convert("RGBA")
        
        # 1. Choose continuous random scale size
        scale = random.uniform(config.image_scale_min, config.image_scale_max)
        w = int(source_flower.width * scale)
        h = int(source_flower.height * scale)
        if w < 15 or h < 15: continue
        
        # Apply random orientation rotations and mirroring
        transformed = source_flower.resize((w, h), Image.Resampling.LANCZOS)
        if random.choice([True, False]):
            transformed = transformed.transpose(Image.FLIP_LEFT_RIGHT)
        transformed = transformed.rotate(random.uniform(0, 360), expand=True, resample=Image.BICUBIC)
        tw, th = transformed.size
        
        # Calculate a protective radius for this specific flower size based on its largest dimension
        flower_radius = (max(tw, th) // 2) + edge_separation_buffer
        
        placed_successfully = False
        
        # 2. Fully Random Placement Engine
        for _ in range(500):
            # Pick any random pixel coordinate across the entire canvas space
            cx = random.randint(0, master_size)
            cy = random.randint(0, master_size)
            
            collision = False
            
            # Verify spacing buffer against all existing items, wrapping over borders seamlessly
            for ex, ey, erady in placed_flowers:
                # Loop through a 3x3 wrap grid to protect seamless repeating margins
                for offset_x in [-master_size, 0, master_size]:
                    for offset_y in [-master_size, 0, master_size]:
                        wrapped_cx = cx + offset_x
                        wrapped_cy = cy + offset_y
                        
                        distance = get_distance((wrapped_cx, wrapped_cy), (ex, ey))
                        # If the distance between centers is smaller than their combined radii, they collide
                        if distance < (flower_radius + erady):
                            collision = True
                            break
                    if collision: break
                if collision: break
            
            # If the spot is safe, lock it down
            if not collision:
                placed_flowers.append((cx, cy, flower_radius))
                placed_successfully = True
                break
                
        # 3. Paste the asset onto the panel canvas along with its repeating border loops
        if placed_successfully:
            x = cx - (tw // 2)
            y = cy - (th // 2)
            
            for offset_x in [-master_size, 0, master_size]:
                for offset_y in [-master_size, 0, master_size]:
                    px = x + offset_x
                    py = y + offset_y
                    
                    if px + tw > 0 and px < master_size and py + th > 0 and py < master_size:
                        overlay = Image.new("RGBA", (master_size, master_size), (0, 0, 0, 0))
                        overlay.paste(transformed, (px, py), transformed)
                        master_canvas = Image.alpha_composite(master_canvas, overlay)
        else:
            print(f"Canvas density limit reached at flower iteration {i}. Skipping to avoid crowding.")

    # Save final panel flat file
    final_output = master_canvas.convert("RGB")
    final_output.save(output_path, "PNG")
    print(f"[pattern_gen] Dynamic organic pattern panel successfully generated: {output_path}")
    return output_path
