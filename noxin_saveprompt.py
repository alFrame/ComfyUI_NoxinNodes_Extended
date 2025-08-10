# ****** ComfyUI_NoxinNodes_Extended | Save Prompt History ******
#
# Creator: Alex Furer - Co-Creator(s): Qwen3 and Claude AI - Original author: Noxin https://github.com/noxinias/ComfyUI_NoxinNodes
#
# Praise, comment, bugs, improvements: https://github.com/alFrame/ComfyUI_NoxinNodes_Extended/issues
#
# LICENSE: MIT License
#
# v0.0.01
#   - Initial release
#
# Description:
# TBD
#
# Usage:
# Simple usage:
# - Use it!
#
# Changelog:
# v0.0.01
# - Inital Git Release#
#
# Feature Requests / Wet Dreams
# - 

import csv
import os
from datetime import datetime
import uuid

class NoxinPromptSave:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        
        return {
            "required": {
                "newprompt": ("STRING", {"default": "","multiline": True}),
                "filename": ("STRING", {"default": "Global_Positive", "multiline": False}),
                "saveprompt": (["on", "off"], ),
                "custom_path": ("STRING", {"default": "AF-Prompt Archive", "multiline": False}),
            },
            "optional": {
                "generation_id": ("STRING", {"default": "", "multiline": False}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("prompt", "generation_id",)

    FUNCTION = "main"
    OUTPUT_NODE = True
    CATEGORY = "NoxinNodes"

    def main(self, newprompt, filename, saveprompt, custom_path, generation_id=""):      
        outStr = newprompt
        
        # Generate or use existing generation_id
        if not generation_id.strip():
            generation_id = str(uuid.uuid4())[:8]  # Short UUID for readability
        
        if saveprompt == "on" and newprompt != "" and newprompt != "Empty Library":   
            csv_filename = filename.strip() + ".csv"
            
            try:
                # Import ComfyUI's folder_paths to get the actual output directory
                import folder_paths
                output_dir = folder_paths.get_output_directory()
            except:
                # Fallback: use default ComfyUI structure if folder_paths import fails
                my_dir = os.path.dirname(os.path.abspath(__file__))
                comfyui_root = os.path.dirname(os.path.dirname(my_dir))
                output_dir = os.path.join(comfyui_root, "output")
            
            library_path = os.path.join(output_dir, custom_path.strip())
            os.makedirs(library_path, exist_ok=True)  # Create directory if it doesn't exist
            csv_file_path = os.path.join(library_path, csv_filename)
            
            # Check if CSV file exists and has headers
            file_exists = os.path.exists(csv_file_path)
            
            try:
                with open(csv_file_path, "a", newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['timestamp', 'generation_id', 'prompt_text']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    # Write header if file is new
                    if not file_exists:
                        writer.writeheader()
                    
                    # Write the prompt data
                    writer.writerow({
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'generation_id': generation_id,
                        'prompt_text': newprompt.replace('\n', '\\n')  # Escape newlines for CSV
                    })
                    
                print(f"Noxin Prompt Save: Saved prompt to {csv_filename} with ID {generation_id}")
                
            except Exception as e:
                print(f"Noxin Prompt Save: Error saving to CSV - {str(e)}")
                
        return (outStr, generation_id,)