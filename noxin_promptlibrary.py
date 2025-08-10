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
import hashlib

# Global cache for dropdown options
_dropdown_cache = {}
_file_timestamps = {}

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
    return csv_files if csv_files else ["No CSV files found"]

def getCacheKey(filename, custom_path, filter_by, limit):
    """Generate a cache key for the dropdown options"""
    return f"{custom_path}:{filename}:{filter_by}:{limit}"

def getFileModTime(csv_file_path):
    """Get file modification time, return 0 if file doesn't exist"""
    try:
        return os.path.getmtime(csv_file_path)
    except:
        return 0

def getPrompts(filename, custom_path="AF-Prompt Archive", filter_by="recent", limit=50):
    """Get prompts from CSV file with caching"""
    if not filename or filename == "No CSV files found" or filename == "":
        return ["Empty Library"]
    
    try:
        import folder_paths
        output_dir = folder_paths.get_output_directory()
    except:
        my_dir = os.path.dirname(os.path.abspath(__file__))
        comfyui_root = os.path.dirname(os.path.dirname(my_dir))
        output_dir = os.path.join(comfyui_root, "output")
    
    library_path = os.path.join(output_dir, custom_path.strip())
    csv_file_path = os.path.join(library_path, filename + ".csv")
    
    if not os.path.exists(csv_file_path):
        return ["Empty Library"]
    
    # Check cache
    cache_key = getCacheKey(filename, custom_path, filter_by, limit)
    current_mod_time = getFileModTime(csv_file_path)
    
    # If we have cached data and file hasn't changed, return cached version
    if (cache_key in _dropdown_cache and 
        cache_key in _file_timestamps and 
        _file_timestamps[cache_key] == current_mod_time):
        return _dropdown_cache[cache_key]
    
    # Generate fresh data
    prompts = []
    try:
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            
            # Sort by timestamp
            if filter_by == "recent":
                rows.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            elif filter_by == "oldest":
                rows.sort(key=lambda x: x.get('timestamp', ''))
            
            # Apply limit
            rows = rows[:limit]
            
            for idx, row in enumerate(rows, 1):
                prompt_text = row.get('prompt_text', '').replace('\\n', '\n')
                timestamp = row.get('timestamp', '')
                generation_id = row.get('generation_id', '')
                
                # Create short preview for dropdown (first 60 chars)
                preview = prompt_text.replace('\n', ' | ')[:60]
                if len(prompt_text) > 60:
                    preview += "..."
                
                # Format: [index] [time] [id] preview
                display_text = f"[{idx}] {timestamp[-8:]} {generation_id[:8]} {preview}"
                prompts.append(display_text)
    
    except Exception as e:
        result = [f"Error: {str(e)}"]
        # Cache error result too
        _dropdown_cache[cache_key] = result
        _file_timestamps[cache_key] = current_mod_time
        return result
    
    result = [""] + prompts if prompts else ["Empty Library"]
    
    # Cache the result
    _dropdown_cache[cache_key] = result
    _file_timestamps[cache_key] = current_mod_time
    
    return result

class NoxinPromptLoad:
    
    def __init__(self):
        pass
        
    @classmethod
    def INPUT_TYPES(s):
        csv_files = getCSVFiles()
        default_file = csv_files[0] if csv_files and csv_files[0] != "No CSV files found" else ""
        
        return {
            "required": {
                "filename": (csv_files, {"default": default_file}),
                "custom_path": ("STRING", {"default": "AF-Prompt Archive", "multiline": False}),
                "filter_by": (["recent", "oldest", "all"], {"default": "recent"}),
                "limit": ("INT", {"default": 20, "min": 1, "max": 100, "step": 1}),
                "refresh_trigger": ("INT", {"default": 0, "min": 0, "max": 999999}),
            },
            "optional": {
                "selected_prompt": ("STRING", {"forceInput": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING",)
    RETURN_NAMES = ("prompt", "generation_id", "timestamp", "available_prompts",)
    
    FUNCTION = "main"
    CATEGORY = "NoxinNodes"
    
    @classmethod
    def IS_CHANGED(cls, filename, custom_path, filter_by, limit, refresh_trigger, **kwargs):
        """Force refresh when parameters change"""
        # Create a hash of all parameters to detect changes
        param_string = f"{filename}:{custom_path}:{filter_by}:{limit}:{refresh_trigger}"
        return hashlib.md5(param_string.encode()).hexdigest()

    def main(self, filename, custom_path, filter_by, limit, refresh_trigger, selected_prompt=None):
        
        # Get available prompts (this will use cache when appropriate)
        available_prompts = getPrompts(filename, custom_path, filter_by, limit)
        available_prompts_str = "\n".join(available_prompts[1:])  # Skip empty first item
        
        if not selected_prompt or selected_prompt == "Empty Library" or selected_prompt == "":
            return ("", "", "", available_prompts_str)
        
        # Parse the display format to extract the actual data
        try:
            # Get the CSV data to find the full prompt
            import folder_paths
            output_dir = folder_paths.get_output_directory()
        except:
            my_dir = os.path.dirname(os.path.abspath(__file__))
            comfyui_root = os.path.dirname(os.path.dirname(my_dir))
            output_dir = os.path.join(comfyui_root, "output")
        
        library_path = os.path.join(output_dir, custom_path.strip())
        csv_file_path = os.path.join(library_path, filename + ".csv")
        
        if not os.path.exists(csv_file_path):
            return ("", "", "", available_prompts_str)
        
        try:
            # Extract index from selected prompt format: [1] timestamp id preview
            if selected_prompt.startswith('['):
                index_end = selected_prompt.find(']')
                if index_end > 0:
                    index = int(selected_prompt[1:index_end]) - 1  # Convert to 0-based
                    
                    # Read CSV and get the actual prompt at that index
                    with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
                        reader = csv.DictReader(csvfile)
                        rows = list(reader)
                        
                        # Apply same sorting as in getPrompts
                        if filter_by == "recent":
                            rows.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                        elif filter_by == "oldest":
                            rows.sort(key=lambda x: x.get('timestamp', ''))
                        
                        rows = rows[:limit]
                        
                        if 0 <= index < len(rows):
                            row = rows[index]
                            prompt_text = row.get('prompt_text', '').replace('\\n', '\n')
                            generation_id = row.get('generation_id', '')
                            timestamp = row.get('timestamp', '')
                            
                            print(f"Noxin Prompt Load: Loaded prompt {index+1} from {filename}.csv")
                            return (prompt_text, generation_id, timestamp, available_prompts_str)
            
        except Exception as e:
            print(f"Noxin Prompt Load: Error parsing selection - {str(e)}")
            return (selected_prompt, "", "", available_prompts_str)
        
        return ("", "", "", available_prompts_str)

# Helper node for prompt selection
class NoxinPromptSelector:
    """Helper node for selecting prompts from the available list"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "available_prompts": ("STRING", {"forceInput": True}),
                "selection_index": ("INT", {"default": 1, "min": 1, "max": 100}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("selected_prompt",)
    
    FUNCTION = "select_prompt"
    CATEGORY = "NoxinNodes"

    def select_prompt(self, available_prompts, selection_index):
        if not available_prompts:
            return ("",)
        
        prompts = available_prompts.strip().split('\n')
        if prompts and len(prompts) >= selection_index:
            return (prompts[selection_index - 1],)
        
        return ("",)

# Export both nodes
NODE_CLASS_MAPPINGS = {
    "NoxinPromptLoad": NoxinPromptLoad,
    "NoxinPromptSelector": NoxinPromptSelector,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "NoxinPromptLoad": "Noxin Prompt Load",
    "NoxinPromptSelector": "Noxin Prompt Selector",
}