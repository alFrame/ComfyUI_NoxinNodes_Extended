# ****** ComfyUI_NoxinNodes_Extended | AF Save Prompt History ******
#
# Creator: Alex Furer - Co-Creator(s): Claude AI - Original author: Noxin https://github.com/noxinias/ComfyUI_NoxinNodes
#
# Praise, comment, bugs, improvements: https://github.com/alFrame/ComfyUI_NoxinNodes_Extended/issues
#
# LICENSE: MIT License
#
# v0.1.0
#   - Switched to YAML format
#   - Fixed duplicate saving issue
#   - Renamed variables from "noxin" to "AF"
#   - Always save prompts regardless of content changes
#
# Description:
# Saves prompt history to YAML files with proper deduplication and timestamp tracking
#
# Usage:
# - Connect your prompt text to newprompt
# - Set filename for the YAML file (without extension)
# - Set saveprompt to "on" to enable saving
# - Optionally provide generation_id for tracking
#
# Changelog:
# v0.1.0
# - Converted from CSV to YAML format
# - Fixed issue where unchanged prompts weren't saved
# - Renamed all "noxin" references to "AF"
# - Improved deduplication logic
# - Better error handling and logging

import yaml
import os
from datetime import datetime
import uuid
import hashlib

class AFPromptSave:
    def __init__(self):
        # Track last saved content per filename to detect actual changes
        self.last_saved_content = {}
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "newprompt": ("STRING", {"default": "","multiline": True}),
                "filename": ("STRING", {"default": "Global_Positive", "multiline": False}),
                "saveprompt": (["on", "off"], ),
                "custom_path": ("STRING", {"default": "AF-Prompt Archive", "multiline": False}),
                "force_save": ("BOOLEAN", {"default": True}),  # Always save by default
            },
            "optional": {
                "generation_id": ("STRING", {"default": "", "multiline": False}),
                "tags": ("STRING", {"default": "", "multiline": False}),  # Optional tags for categorization
                "notes": ("STRING", {"default": "", "multiline": False}),  # Optional notes
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING",)
    RETURN_NAMES = ("prompt", "generation_id", "yaml_filepath",)

    FUNCTION = "main"
    OUTPUT_NODE = True
    CATEGORY = "AF Nodes"

    def load_existing_yaml(self, yaml_file_path):
        """Load existing YAML data or return empty structure"""
        if os.path.exists(yaml_file_path):
            try:
                with open(yaml_file_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                    # Ensure proper structure
                    if 'prompts' not in data:
                        data['prompts'] = []
                    if 'metadata' not in data:
                        data['metadata'] = {
                            'created': datetime.now().isoformat(),
                            'total_prompts': 0,
                            'last_updated': datetime.now().isoformat()
                        }
                    return data
            except Exception as e:
                print(f"AF Prompt Save: Error loading existing YAML - {str(e)}")
                # Return fresh structure on error
                pass
        
        # Return fresh structure
        return {
            'metadata': {
                'created': datetime.now().isoformat(),
                'total_prompts': 0,
                'last_updated': datetime.now().isoformat(),
                'file_version': '1.0'
            },
            'prompts': []
        }

    def should_save_prompt(self, newprompt, filename, force_save):
        """Determine if prompt should be saved"""
        if not newprompt or newprompt.strip() == "" or newprompt == "Empty Library":
            return False
        
        if force_save:
            return True
        
        # Check if content actually changed since last save
        content_hash = hashlib.md5(newprompt.encode()).hexdigest()
        last_hash = self.last_saved_content.get(filename)
        
        if last_hash != content_hash:
            self.last_saved_content[filename] = content_hash
            return True
        
        return False

    def find_duplicate_prompt(self, prompts_list, newprompt, generation_id=""):
        """Check if prompt already exists to avoid true duplicates"""
        content_hash = hashlib.md5(newprompt.strip().encode()).hexdigest()
        
        for prompt in prompts_list:
            existing_hash = hashlib.md5(prompt.get('text', '').strip().encode()).hexdigest()
            if existing_hash == content_hash:
                # If generation_id matches too, it's definitely a duplicate
                if generation_id and prompt.get('generation_id') == generation_id:
                    return prompt
                # If content is identical and recent (within last hour), likely duplicate
                try:
                    existing_time = datetime.fromisoformat(prompt.get('timestamp', ''))
                    time_diff = datetime.now() - existing_time
                    if time_diff.total_seconds() < 3600:  # 1 hour
                        return prompt
                except:
                    pass
        
        return None

    def main(self, newprompt, filename, saveprompt, custom_path, force_save=True, generation_id="", tags="", notes=""):      
        outStr = newprompt
        yaml_filepath = ""
        
        # Generate or use existing generation_id
        if not generation_id.strip():
            generation_id = str(uuid.uuid4())[:8]  # Short UUID for readability
        
        # Check if we should save
        if saveprompt == "on" and self.should_save_prompt(newprompt, filename, force_save):   
            yaml_filename = filename.strip() + ".yaml"
            
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
            yaml_file_path = os.path.join(library_path, yaml_filename)
            yaml_filepath = yaml_file_path
            
            try:
                # Load existing data
                yaml_data = self.load_existing_yaml(yaml_file_path)
                
                # Check for duplicates (but still save if force_save is True)
                duplicate = self.find_duplicate_prompt(yaml_data['prompts'], newprompt, generation_id)
                
                if duplicate and not force_save:
                    print(f"AF Prompt Save: Duplicate prompt found, skipping save")
                    return (outStr, duplicate.get('generation_id', generation_id), yaml_filepath)
                
                # Prepare new prompt entry
                new_prompt = {
                    'text': newprompt,
                    'timestamp': datetime.now().isoformat(),
                    'generation_id': generation_id,
                    'content_hash': hashlib.md5(newprompt.strip().encode()).hexdigest()[:8]  # Short hash for reference
                }
                
                # Add optional fields if provided
                if tags.strip():
                    new_prompt['tags'] = [tag.strip() for tag in tags.split(',') if tag.strip()]
                
                if notes.strip():
                    new_prompt['notes'] = notes.strip()
                
                # Add workflow info if available
                try:
                    new_prompt['saved_from'] = {
                        'node_type': 'AF_Save_Prompt_History',
                        'filename': filename,
                        'custom_path': custom_path
                    }
                except:
                    pass
                
                # Add to prompts list
                yaml_data['prompts'].append(new_prompt)
                
                # Update metadata
                yaml_data['metadata']['total_prompts'] = len(yaml_data['prompts'])
                yaml_data['metadata']['last_updated'] = datetime.now().isoformat()
                
                # Save YAML file with nice formatting
                with open(yaml_file_path, 'w', encoding='utf-8') as yamlfile:
                    yaml.dump(yaml_data, yamlfile, 
                             default_flow_style=False, 
                             allow_unicode=True, 
                             indent=2, 
                             sort_keys=False)
                    
                print(f"AF Prompt Save: Saved prompt to {yaml_filename} with ID {generation_id}")
                
                # Log save stats
                total_prompts = len(yaml_data['prompts'])
                if duplicate:
                    print(f"AF Prompt Save: Saved despite duplicate (force_save=True). Total prompts: {total_prompts}")
                else:
                    print(f"AF Prompt Save: New unique prompt saved. Total prompts: {total_prompts}")
                
            except Exception as e:
                print(f"AF Prompt Save: Error saving to YAML - {str(e)}")
                import traceback
                traceback.print_exc()
        
        elif saveprompt == "on":
            print(f"AF Prompt Save: Skipping save - no changes detected or empty prompt")
                
        return (outStr, generation_id, yaml_filepath)

# Also provide a utility node for YAML management
class AFPromptYAMLManager:
    """Utility node for managing YAML prompt files"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "action": (["merge_files", "deduplicate", "backup", "stats"], {"default": "stats"}),
                "filename": ("STRING", {"default": "Global_Positive", "multiline": False}),
                "custom_path": ("STRING", {"default": "AF-Prompt Archive", "multiline": False}),
            },
            "optional": {
                "merge_target": ("STRING", {"default": "", "multiline": False}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("result", "details",)

    FUNCTION = "manage_yaml"
    OUTPUT_NODE = True
    CATEGORY = "AF Nodes"

    def manage_yaml(self, action, filename, custom_path, merge_target=""):
        try:
            import folder_paths
            output_dir = folder_paths.get_output_directory()
        except:
            my_dir = os.path.dirname(os.path.abspath(__file__))
            comfyui_root = os.path.dirname(os.path.dirname(my_dir))
            output_dir = os.path.join(comfyui_root, "output")
        
        library_path = os.path.join(output_dir, custom_path.strip())
        yaml_file_path = os.path.join(library_path, filename + ".yaml")
        
        if not os.path.exists(yaml_file_path):
            return ("Error", f"File {filename}.yaml not found")
        
        try:
            with open(yaml_file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            
            if action == "stats":
                prompts = data.get('prompts', [])
                metadata = data.get('metadata', {})
                
                stats = {
                    'total_prompts': len(prompts),
                    'created': metadata.get('created', 'Unknown'),
                    'last_updated': metadata.get('last_updated', 'Unknown'),
                    'unique_generation_ids': len(set(p.get('generation_id', '') for p in prompts)),
                    'tagged_prompts': len([p for p in prompts if p.get('tags')]),
                    'prompts_with_notes': len([p for p in prompts if p.get('notes')])
                }
                
                details = yaml.dump(stats, default_flow_style=False)
                return ("Stats Generated", details)
            
            elif action == "deduplicate":
                prompts = data.get('prompts', [])
                unique_prompts = []
                seen_hashes = set()
                
                for prompt in prompts:
                    content_hash = hashlib.md5(prompt.get('text', '').strip().encode()).hexdigest()
                    if content_hash not in seen_hashes:
                        unique_prompts.append(prompt)
                        seen_hashes.add(content_hash)
                
                removed = len(prompts) - len(unique_prompts)
                data['prompts'] = unique_prompts
                data['metadata']['total_prompts'] = len(unique_prompts)
                data['metadata']['last_updated'] = datetime.now().isoformat()
                
                with open(yaml_file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True, indent=2)
                
                return ("Deduplicated", f"Removed {removed} duplicate prompts")
            
            elif action == "backup":
                backup_name = f"{filename}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
                backup_path = os.path.join(library_path, backup_name)
                
                with open(backup_path, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True, indent=2)
                
                return ("Backup Created", f"Backup saved as {backup_name}")
            
            else:
                return ("Error", f"Action {action} not implemented yet")
                
        except Exception as e:
            return ("Error", str(e))

# Node mappings for ComfyUI
NODE_CLASS_MAPPINGS = {
    "AFPromptSave": AFPromptSave,
    "AFPromptYAMLManager": AFPromptYAMLManager,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AFPromptSave": "AF Save Prompt History",
    "AFPromptYAMLManager": "AF Prompt YAML Manager",
}