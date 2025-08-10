# ****** ComfyUI_NoxinNodes_Extended | Load Prompt History ******
#
# Creator: Alex Furer | Co-Creator(s): Claude AI | Original author: Noxin https://github.com/noxinias/ComfyUI_NoxinNodes
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


import os
import csv
from datetime import datetime

def getCSVFiles(custom_path="AF-Prompt Archive"):
    """Get list of available CSV files"""
    try:
        import folder_paths
        output_dir = folder_paths.get_output_directory()
    except:
        # Fallback
        my_dir = os.path.dirname(os.path.abspath(__file__))
        comfyui_root = os.path.dirname(os.path.dirname(my_dir))
        output_dir = os.path.join(comfyui_root, "output")
    
    library_path = os.path.join(output_dir, custom_path.strip())
    
    if not os.path.exists(library_path):
        return ["No CSV files found"]
    
    csv_files = [f[:-4] for f in os.listdir(library_path) if f.endswith('.csv')]
    return [""] + csv_files if csv_files else ["No CSV files found"]

def getPrompts(filename, custom_path="AF-Prompt Archive", filter_by="recent", limit=50):
    """Get prompts from CSV file with various filtering options"""
    if not filename or filename == "No CSV files found":
        return ["Empty Library"]
    
    try:
        import folder_paths
        output_dir = folder_paths.get_output_directory()
    except:
        # Fallback
        my_dir = os.path.dirname(os.path.abspath(__file__))
        comfyui_root = os.path.dirname(os.path.dirname(my_dir))
        output_dir = os.path.join(comfyui_root, "output")
    
    library_path = os.path.join(output_dir, custom_path.strip())
    csv_file_path = os.path.join(library_path, filename + ".csv")
    
    if not os.path.exists(csv_file_path):
        return ["Empty Library"]
    
    prompts = []
    try:
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            
            # Sort by timestamp (newest first for recent)
            if filter_by == "recent":
                rows.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            elif filter_by == "oldest":
                rows.sort(key=lambda x: x.get('timestamp', ''))
            # For "all", keep original order
            
            # Limit results
            rows = rows[:limit]
            
            for row in rows:
                prompt_text = row.get('prompt_text', '').replace('\\n', '\n')  # Restore newlines
                timestamp = row.get('timestamp', '')
                generation_id = row.get('generation_id', '')
                
                # Format: [timestamp] [gen_id] prompt
                display_text = f"[{timestamp}] [{generation_id}] {prompt_text}"
                prompts.append(display_text)
    
    except Exception as e:
        return [f"Error reading file: {str(e)}"]
    
    return [""] + prompts if prompts else ["Empty Library"]

class NoxinPromptLoad:
    
    def __init__(self):
        pass
        
    @classmethod
    def INPUT_TYPES(s):
        
        return {
            "required": {
                "filename": (getCSVFiles(), {"default": ""}),
                "custom_path": ("STRING", {"default": "AF-Prompt Archive", "multiline": False}),
                "filter_by": (["recent", "oldest", "all"], {"default": "recent"}),
                "limit": ("INT", {"default": 50, "min": 1, "max": 500, "step": 1}),
                "selected_prompt": ([""], {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING",)
    RETURN_NAMES = ("prompt", "generation_id", "timestamp",)
    
    FUNCTION = "main"
    CATEGORY = "NoxinNodes"   

    def main(self, filename, custom_path, filter_by, limit, selected_prompt):
        
        if not selected_prompt or selected_prompt == "Empty Library":
            return ("", "", "")
        
        # Parse the selected prompt format: [timestamp] [gen_id] prompt
        try:
            # Extract timestamp
            timestamp_end = selected_prompt.find('] [')
            if timestamp_end == -1:
                return (selected_prompt, "", "")
            
            timestamp = selected_prompt[1:timestamp_end]  # Remove first '['
            
            # Extract generation_id
            gen_id_start = timestamp_end + 3  # Skip '] ['
            gen_id_end = selected_prompt.find('] ', gen_id_start)
            if gen_id_end == -1:
                return (selected_prompt, "", timestamp)
            
            generation_id = selected_prompt[gen_id_start:gen_id_end]
            
            # Extract actual prompt text
            prompt_text = selected_prompt[gen_id_end + 2:]  # Skip '] '
            
            return (prompt_text, generation_id, timestamp)
            
        except Exception as e:
            # Fallback: return the whole thing as prompt
            return (selected_prompt, "", "")

# Dynamic update function for the dropdown
def update_prompt_dropdown(filename, custom_path, filter_by, limit):
    """This would be called when filename changes to update the prompt dropdown"""
    return {"selected_prompt": (getPrompts(filename, custom_path, filter_by, limit), {"default": ""})}

# Note: ComfyUI doesn't support dynamic dropdown updates in the current version,
# so users will need to refresh the node or restart ComfyUI when changing files