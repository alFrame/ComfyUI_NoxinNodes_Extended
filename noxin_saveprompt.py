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
            
            # Read existing lines, create empty list if file doesn't exist
            lines = []
            if os.path.exists(library_path):
                lines = open(library_path, "r").read().splitlines()
            
            if newprompt in lines:
                print("Noxin Prompt Save: Prompt already exists")
            else:
                print("Noxin Prompt Save: Adding new prompt")
                f = open(library_path, "a+")
                f.write(newprompt + "\n")
                f.close()               
                
        return (outStr,)