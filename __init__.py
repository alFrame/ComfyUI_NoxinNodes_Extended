# Import from your actual AF modules
from .af_load_prompt_history import *
from .af_save_prompt_history import *

# Import from existing noxin modules (if they still exist)
from .noxin_chimenode import *
from .noxin_scaledresolution import *
from .noxin_saveprompt import *
from .noxin_simplemath import *
from .noxin_splitprompt import *

# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    # AF Nodes
    "AFPromptLoad": AFPromptLoad,
    "AFPromptSave": AFPromptSave,
    "AFPromptSearch": AFPromptSearch,
    "AFPromptYAMLManager": AFPromptYAMLManager,
    
    # Original Noxin Nodes (if they still exist)
    "NoxinChime": NoxinChime,
    "NoxinScaledResolution": NoxinScaledResolution,
    "NoxinSimpleMath": NoxinSimpleMath,
    "NoxinSplitPrompt": NoxinSplitPrompt
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    # AF Nodes
    "AFPromptLoad": "AF Load Prompt History",
    "AFPromptSave": "AF Save Prompt History", 
    "AFPromptSearch": "AF Prompt Search",
    "AFPromptYAMLManager": "AF Prompt YAML Manager",
    
    # Original Noxin Nodes (if they still exist)
    "NoxinChime": "Noxin Complete Chime",
    "NoxinScaledResolution": "Noxin Scaled Resolutions",
    "NoxinSimpleMath": "Simple Math Operations",
    "NoxinSplitPrompt": "Split Prompt Organiser"
}