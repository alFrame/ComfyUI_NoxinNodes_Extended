# ****** ComfyUI_NoxinNodes_Extended | AF Load Prompt History ******
#
# Creator: Alex Furer | Co-Creator(s): Claude AI | Original author: Noxin https://github.com/noxinias/ComfyUI_NoxinNodes
#
# LICENSE: MIT License
#
# v0.1.0
#   - Converted to YAML format
#   - Renamed from "noxin" to "AF"
#   - Improved dynamic dropdown handling
#   - Added search and filter capabilities
#
# Description:
# Loads prompt history from YAML files with dynamic dropdown refresh and search capabilities
#
# Usage:
# - Select YAML file from dropdown
# - Choose filter and limit options
# - Select specific prompt from the list
# - Connect outputs to your workflow

import os
import yaml
from datetime import datetime
import hashlib
import re

# Global cache for dropdown options
_af_dropdown_cache = {}
_af_file_timestamps = {}

def getAFYAMLFiles(custom_path="AF-Prompt Archive"):
    """Get list of available YAML files"""
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
        return ["No YAML files found"]
    
    yaml_files = []
    for f in os.listdir(library_path):
        if f.endswith(('.yaml', '.yml')):
            # Remove extension for display
            name = f[:-5] if f.endswith('.yaml') else f[:-4]
            yaml_files.append(name)
    
    return sorted(yaml_files) if yaml_files else ["No YAML files found"]

def getAFCacheKey(filename, custom_path, filter_by, limit, search_term=""):
    """Generate a cache key for the dropdown options"""
    return f"{custom_path}:{filename}:{filter_by}:{limit}:{search_term}"

def getAFFileModTime(yaml_file_path):
    """Get file modification time, return 0 if file doesn't exist"""
    try:
        return os.path.getmtime(yaml_file_path)
    except:
        return 0

def searchInPrompt(prompt_data, search_term):
    """Search within a prompt entry"""
    if not search_term:
        return True
    
    search_term = search_term.lower()
    
    # Search in text
    if search_term in prompt_data.get('text', '').lower():
        return True
    
    # Search in tags
    tags = prompt_data.get('tags', [])
    if isinstance(tags, list):
        for tag in tags:
            if search_term in str(tag).lower():
                return True
    
    # Search in notes
    notes = prompt_data.get('notes', '')
    if search_term in notes.lower():
        return True
    
    # Search in generation_id
    gen_id = prompt_data.get('generation_id', '')
    if search_term in gen_id.lower():
        return True
    
    return False

def getAFPrompts(filename, custom_path="AF-Prompt Archive", filter_by="recent", limit=50, search_term=""):
    """Get prompts from YAML file with caching and search"""
    if not filename or filename == "No YAML files found" or filename == "":
        return ["Empty Library"]
    
    try:
        import folder_paths
        output_dir = folder_paths.get_output_directory()
    except:
        my_dir = os.path.dirname(os.path.abspath(__file__))
        comfyui_root = os.path.dirname(os.path.dirname(my_dir))
        output_dir = os.path.join(comfyui_root, "output")
    
    library_path = os.path.join(output_dir, custom_path.strip())
    
    # Try both extensions
    yaml_file_path = None
    for ext in ['.yaml', '.yml']:
        test_path = os.path.join(library_path, filename + ext)
        if os.path.exists(test_path):
            yaml_file_path = test_path
            break
    
    if not yaml_file_path:
        return ["Empty Library"]
    
    # Check cache
    cache_key = getAFCacheKey(filename, custom_path, filter_by, limit, search_term)
    current_mod_time = getAFFileModTime(yaml_file_path)
    
    # If we have cached data and file hasn't changed, return cached version
    if (cache_key in _af_dropdown_cache and 
        cache_key in _af_file_timestamps and 
        _af_file_timestamps[cache_key] == current_mod_time):
        return _af_dropdown_cache[cache_key]
    
    # Generate fresh data
    prompts = []
    try:
        with open(yaml_file_path, 'r', encoding='utf-8') as yamlfile:
            data = yaml.safe_load(yamlfile) or {}
            
        # Extract prompts from YAML structure
        prompts_data = data.get('prompts', [])
        
        # Filter by search term first
        if search_term.strip():
            prompts_data = [p for p in prompts_data if searchInPrompt(p, search_term.strip())]
        
        # Sort by timestamp or other criteria
        if filter_by == "recent":
            prompts_data.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        elif filter_by == "oldest":
            prompts_data.sort(key=lambda x: x.get('timestamp', ''))
        elif filter_by == "alphabetical":
            prompts_data.sort(key=lambda x: x.get('text', '').lower())
        
        # Apply limit
        prompts_data = prompts_data[:limit]
        
        for idx, prompt_data in enumerate(prompts_data, 1):
            prompt_text = prompt_data.get('text', '')
            timestamp = prompt_data.get('timestamp', '')
            generation_id = prompt_data.get('generation_id', '')
            tags = prompt_data.get('tags', [])
            
            # Create short preview for dropdown (first 60 chars)
            preview = prompt_text.replace('\n', ' | ')[:60]
            if len(prompt_text) > 60:
                preview += "..."
            
            # Add tags to preview if available
            if tags and isinstance(tags, list):
                tags_str = " #" + " #".join(tags[:2])  # Show first 2 tags
                if len(preview) + len(tags_str) <= 80:
                    preview += tags_str
            
            # Format timestamp for display
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_display = dt.strftime("%m-%d %H:%M")
            except:
                time_display = timestamp[-8:] if timestamp else "no-time"
            
            # Format: [index] [time] [id] preview
            gen_id_display = generation_id[:8] if generation_id else "no-id"
            display_text = f"[{idx}] {time_display} {gen_id_display} {preview}"
            prompts.append(display_text)
    
    except Exception as e:
        result = [f"Error: {str(e)}"]
        # Cache error result too
        _af_dropdown_cache[cache_key] = result
        _af_file_timestamps[cache_key] = current_mod_time
        return result
    
    result = [""] + prompts if prompts else ["Empty Library"]
    
    # Cache the result
    _af_dropdown_cache[cache_key] = result
    _af_file_timestamps[cache_key] = current_mod_time
    
    return result

class AFPromptLoad:
    
    def __init__(self):
        pass
        
    @classmethod
    def INPUT_TYPES(s):
        yaml_files = getAFYAMLFiles()
        default_file = yaml_files[0] if yaml_files and yaml_files[0] != "No YAML files found" else ""
        
        return {
            "required": {
                "filename": (yaml_files, {"default": default_file}),
                "custom_path": ("STRING", {"default": "AF-Prompt Archive", "multiline": False}),
                "filter_by": (["recent", "oldest", "alphabetical", "all"], {"default": "recent"}),
                "limit": ("INT", {"default": 20, "min": 1, "max": 100, "step": 1}),
                "selected_prompt": (getAFPrompts(default_file), {"default": ""}),
            },
            "optional": {
                "search_term": ("STRING", {"default": "", "multiline": False}),
                "refresh_trigger": ("INT", {"default": 0, "min": 0, "max": 999999}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING",)
    RETURN_NAMES = ("prompt", "generation_id", "timestamp", "tags", "notes",)
    
    FUNCTION = "main"
    CATEGORY = "AF Nodes"
    
    @classmethod
    def IS_CHANGED(cls, filename, custom_path, filter_by, limit, selected_prompt, search_term="", refresh_trigger=0, **kwargs):
        """Force refresh when parameters change"""
        # Create a hash of all parameters to detect changes
        param_string = f"{filename}:{custom_path}:{filter_by}:{limit}:{search_term}:{refresh_trigger}"
        
        # Also check file modification time
        try:
            import folder_paths
            output_dir = folder_paths.get_output_directory()
        except:
            my_dir = os.path.dirname(os.path.abspath(__file__))
            comfyui_root = os.path.dirname(os.path.dirname(my_dir))
            output_dir = os.path.join(comfyui_root, "output")
        
        library_path = os.path.join(output_dir, custom_path.strip())
        
        for ext in ['.yaml', '.yml']:
            yaml_file_path = os.path.join(library_path, filename + ext)
            if os.path.exists(yaml_file_path):
                try:
                    mod_time = os.path.getmtime(yaml_file_path)
                    param_string += f":{mod_time}"
                    break
                except:
                    pass
        
        return hashlib.md5(param_string.encode()).hexdigest()

    def main(self, filename, custom_path, filter_by, limit, selected_prompt, search_term="", refresh_trigger=0):
        
        if not selected_prompt or selected_prompt == "Empty Library" or selected_prompt == "":
            return ("", "", "", "", "")
        
        # Parse the display format to extract the actual data
        try:
            # Get the YAML data to find the full prompt
            import folder_paths
            output_dir = folder_paths.get_output_directory()
        except:
            my_dir = os.path.dirname(os.path.abspath(__file__))
            comfyui_root = os.path.dirname(os.path.dirname(my_dir))
            output_dir = os.path.join(comfyui_root, "output")
        
        library_path = os.path.join(output_dir, custom_path.strip())
        
        # Find the YAML file
        yaml_file_path = None
        for ext in ['.yaml', '.yml']:
            test_path = os.path.join(library_path, filename + ext)
            if os.path.exists(test_path):
                yaml_file_path = test_path
                break
        
        if not yaml_file_path:
            return ("", "", "", "", "")
        
        try:
            # Extract index from selected prompt format: [1] timestamp id preview
            if selected_prompt.startswith('['):
                index_end = selected_prompt.find(']')
                if index_end > 0:
                    index = int(selected_prompt[1:index_end]) - 1  # Convert to 0-based
                    
                    # Read YAML and get the actual prompt at that index
                    with open(yaml_file_path, 'r', encoding='utf-8') as yamlfile:
                        data = yaml.safe_load(yamlfile) or {}
                        
                    prompts_data = data.get('prompts', [])
                    
                    # Apply same filtering and searching as in getAFPrompts
                    if search_term.strip():
                        prompts_data = [p for p in prompts_data if searchInPrompt(p, search_term.strip())]
                    
                    # Apply same sorting as in getAFPrompts
                    if filter_by == "recent":
                        prompts_data.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                    elif filter_by == "oldest":
                        prompts_data.sort(key=lambda x: x.get('timestamp', ''))
                    elif filter_by == "alphabetical":
                        prompts_data.sort(key=lambda x: x.get('text', '').lower())
                    
                    prompts_data = prompts_data[:limit]
                    
                    if 0 <= index < len(prompts_data):
                        prompt_data = prompts_data[index]
                        prompt_text = prompt_data.get('text', '')
                        generation_id = prompt_data.get('generation_id', '')
                        timestamp = prompt_data.get('timestamp', '')
                        tags = prompt_data.get('tags', [])
                        notes = prompt_data.get('notes', '')
                        
                        # Format tags as string
                        tags_str = ", ".join(tags) if isinstance(tags, list) else str(tags) if tags else ""
                        
                        print(f"AF Prompt Load: Loaded prompt {index+1} from {filename}.yaml")
                        return (prompt_text, generation_id, timestamp, tags_str, notes)
            
        except Exception as e:
            print(f"AF Prompt Load: Error parsing selection - {str(e)}")
            return (selected_prompt, "", "", "", "")
        
        return ("", "", "", "", "")

# Utility node for advanced prompt operations
class AFPromptSearch:
    """Advanced search and filter node for prompt libraries"""
    
    @classmethod
    def INPUT_TYPES(s):
        yaml_files = getAFYAMLFiles()
        default_file = yaml_files[0] if yaml_files and yaml_files[0] != "No YAML files found" else ""
        
        return {
            "required": {
                "filename": (yaml_files, {"default": default_file}),
                "custom_path": ("STRING", {"default": "AF-Prompt Archive", "multiline": False}),
                "search_term": ("STRING", {"default": "", "multiline": False}),
                "search_in": (["text", "tags", "notes", "all"], {"default": "all"}),
                "limit": ("INT", {"default": 10, "min": 1, "max": 50, "step": 1}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("search_results", "count",)
    
    FUNCTION = "search_prompts"
    CATEGORY = "AF Nodes"

    def search_prompts(self, filename, custom_path, search_term, search_in, limit):
        if not filename or filename == "No YAML files found" or not search_term.strip():
            return ("No results", "0")
        
        try:
            import folder_paths
            output_dir = folder_paths.get_output_directory()
        except:
            my_dir = os.path.dirname(os.path.abspath(__file__))
            comfyui_root = os.path.dirname(os.path.dirname(my_dir))
            output_dir = os.path.join(comfyui_root, "output")
        
        library_path = os.path.join(output_dir, custom_path.strip())
        
        # Find YAML file
        yaml_file_path = None
        for ext in ['.yaml', '.yml']:
            test_path = os.path.join(library_path, filename + ext)
            if os.path.exists(test_path):
                yaml_file_path = test_path
                break
        
        if not yaml_file_path:
            return ("File not found", "0")
        
        try:
            with open(yaml_file_path, 'r', encoding='utf-8') as yamlfile:
                data = yaml.safe_load(yamlfile) or {}
            
            prompts_data = data.get('prompts', [])
            search_term_lower = search_term.lower()
            results = []
            
            for idx, prompt_data in enumerate(prompts_data):
                match = False
                
                if search_in == "all" or search_in == "text":
                    if search_term_lower in prompt_data.get('text', '').lower():
                        match = True
                
                if search_in == "all" or search_in == "tags":
                    tags = prompt_data.get('tags', [])
                    if isinstance(tags, list):
                        for tag in tags:
                            if search_term_lower in str(tag).lower():
                                match = True
                                break
                
                if search_in == "all" or search_in == "notes":
                    notes = prompt_data.get('notes', '')
                    if search_term_lower in notes.lower():
                        match = True
                
                if match:
                    # Format result
                    text = prompt_data.get('text', '')
                    preview = text.replace('\n', ' | ')[:80]
                    if len(text) > 80:
                        preview += "..."
                    
                    timestamp = prompt_data.get('timestamp', '')
                    gen_id = prompt_data.get('generation_id', '')
                    
                    result_line = f"[{len(results)+1}] {gen_id[:8]} {preview}"
                    results.append(result_line)
                    
                    if len(results) >= limit:
                        break
            
            if results:
                results_text = "\n".join(results)
                count = str(len(results))
            else:
                results_text = "No matches found"
                count = "0"
            
            return (results_text, count)
            
        except Exception as e:
            return (f"Error: {str(e)}", "0")

# Node mappings for ComfyUI
NODE_CLASS_MAPPINGS = {
    "AFPromptLoad": AFPromptLoad,
    "AFPromptSearch": AFPromptSearch,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AFPromptLoad": "AF Load Prompt History",
    "AFPromptSearch": "AF Prompt Search",
}