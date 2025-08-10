class NoxinPromptSave:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        
        return {
            "required": {
                "newprompt": ("STRING", {"default": "","multiline": True}),
                "librarynum": ("INT", {"default": 1, "min": 1, "max": 6, "step": 1}),
                "saveprompt": (["on", "off"], ),
            },
        }

    RETURN_TYPES = ("STRING",)

    FUNCTION = "main"
    OUTPUT_NODE = True
    CATEGORY = "NoxinNodes"

    def main(self, newprompt, saveprompt, librarynum):      
        outStr = newprompt
        
        if saveprompt == "on" and newprompt != "" and newprompt != "Empty Library":   
            libraryFile = "promptlibrary" + str(librarynum) + ".txt"
            
            import os
            try:
                # Import ComfyUI's folder_paths to get the actual output directory
                import folder_paths
                output_dir = folder_paths.get_output_directory()
            except:
                # Fallback: use default ComfyUI structure if folder_paths import fails
                my_dir = os.path.dirname(os.path.abspath(__file__))
                comfyui_root = os.path.dirname(os.path.dirname(my_dir))
                output_dir = os.path.join(comfyui_root, "output")
            
            library_path = os.path.join(output_dir, "AF-Prompt Archive")
            os.makedirs(library_path, exist_ok=True)  # Create directory if it doesn't exist
            library_path = os.path.join(library_path, libraryFile)        
            
            # Read existing prompts, create empty list if file doesn't exist
            existing_prompts = []
            if os.path.exists(library_path):
                with open(library_path, "r") as f:
                    content = f.read()
                    # Split by double newlines to separate individual prompts
                    existing_prompts = [p.replace("\\n", "\n") for p in content.split("||PROMPT_END||\n") if p.strip()]
            
            # Check if this exact prompt already exists
            if newprompt in existing_prompts:
                print("Noxin Prompt Save: Prompt already exists")
            else:
                print("Noxin Prompt Save: Adding new prompt")
                # Save the prompt with newlines escaped and add delimiter
                prompt_to_save = newprompt.replace("\n", "\\n") + "||PROMPT_END||\n"
                with open(library_path, "a+") as f:
                    f.write(prompt_to_save)               
                
        return (outStr,)