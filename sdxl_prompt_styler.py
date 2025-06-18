import os
import pathlib
import json

# --- Data loader and template logic ---

class Template:
    def __init__(self, prompt, negative_prompt=None):
        self.prompt = prompt
        self.negative_prompt = negative_prompt or ""

    def replace_prompts(self, positive_prompt, negative_prompt, style_weight=2.0, offset=0):
        prompt_str = self.prompt
        # Always ensure {prompt} is present for offset==0
        if "{prompt}" not in prompt_str:
            prompt_str = prompt_str + " {prompt}"

        tokens = prompt_str.split()

        if offset == 0:
            # Join and replace {prompt} in the string (not just tokens)
            prompt_filled = " ".join(tokens)
            prompt_filled = prompt_filled.replace("{prompt}", positive_prompt, 1)
        else:
            # Remove all {prompt} from tokens
            tokens = [tok for tok in tokens if tok != "{prompt}"]
            if offset > 0:
                insert_idx = min(offset, len(tokens))
            else:
                insert_idx = len(tokens) + offset
                if insert_idx < 0:
                    insert_idx = 0
            tokens = tokens[:insert_idx] + [positive_prompt] + tokens[insert_idx:]
            prompt_filled = " ".join(tokens)
            # ENSURE ALL "{prompt}" are removed from the output!
            prompt_filled = prompt_filled.replace("{prompt}", "")

        # Now, weight everything except the user prompt itself
        user_idx = prompt_filled.find(positive_prompt)
        before = prompt_filled[:user_idx].strip(" ,")
        after = prompt_filled[user_idx + len(positive_prompt):].strip(" ,")

        weighted_before = f'("{before}":{style_weight}) ' if before else ""
        weighted_after = f' ("{after}":{style_weight})' if after else ""
        positive_result = f'{weighted_before}{positive_prompt}{weighted_after}'.strip()
        negative_result = ", ".join(x for x in (self.negative_prompt, negative_prompt) if x)
        return positive_result, negative_result

class StylerData:
    def __init__(self, data_dir):
        self.data = {}
        self.menus = []
        self.menu_label_map = {}
        self.load_data(data_dir)

    def load_data(self, data_dir):
        data_path = pathlib.Path(__file__).parent / data_dir
        if not data_path.exists():
            print(f"[PromptStyler] Data folder not found: {data_path}")
            return
        for folder in data_path.iterdir():
            if folder.is_dir():
                menu_name = folder.name
                self.menus.append(menu_name)
                self.data[menu_name] = {}
                for item in folder.glob("*.json"):
                    with open(item, encoding="utf-8") as f:
                        j = json.load(f)
                        for entry in j:
                            template_name = entry.get("name")
                            prompt = entry.get("prompt", "")
                            negative_prompt = entry.get("negative_prompt", "")
                            self.data[menu_name][template_name] = Template(prompt, negative_prompt)
        # Load menu labels if present
        labels_path = data_path / "menu_labels.json"
        if labels_path.exists():
            with open(labels_path, encoding="utf-8") as f:
                self.menu_label_map = json.load(f)

    def get_menu_label(self, menu):
        return self.menu_label_map.get(menu, menu)

    def __getitem__(self, menu):
        return self.data[menu]

def load_combo_config():
    config_path = pathlib.Path(__file__).parent / "styler_config.json"
    combos = {}
    if config_path.exists():
        with open(config_path, encoding="utf-8") as f:
            combos = json.load(f)
    return combos

def make_styler_node_class(node_name, menus):
    menu_fields = {menu: (["none"] + list(styler_data[menu].keys()), ) for menu in menus}
    menu_weight_fields = {f"style_weight_{menu}": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.05}) for menu in menus}
    menu_offset_fields = {f"offset_{menu}": ("INT", {"default": 0, "min": -200.0, "max": 200.0, "step": 1}) for menu in menus}

    class CustomPromptStyler:
        @classmethod
        def INPUT_TYPES(cls):
            fields = {
                "required": {
                    "text_positive": ("STRING", {"default": "", "multiline": True}),
                    "text_negative": ("STRING", {"default": "", "multiline": True}),
                    **menu_fields,
                    **menu_weight_fields,
                    **menu_offset_fields,
                    "log_prompt": ("BOOLEAN", {"default": True, "label_on": "Yes", "label_off": "No"}),
                },
            }
            return fields

        RETURN_TYPES = ("STRING", "STRING",)
        RETURN_NAMES = ("text_positive", "text_negative",)
        FUNCTION = "prompt_styler"
        CATEGORY = "MileHighStyler"

        def prompt_styler(self, text_positive, text_negative, log_prompt=True, **kwargs):
            styled_pos = text_positive
            styled_neg = text_negative
            for menu in menus:
                selection = kwargs.get(menu, "none")
                if selection and selection != "none":
                    weight = kwargs.get(f"style_weight_{menu}", 2.0)
                    offset = kwargs.get(f"offset_{menu}", 0)
                    template = styler_data[menu][selection]
                    styled_pos, styled_neg = template.replace_prompts(
                        styled_pos, styled_neg, style_weight=weight, offset=offset
                    )
            if log_prompt:
                print(f"[PromptStyler:{node_name}] Final prompt: {styled_pos}")
            return (styled_pos, styled_neg)

    CustomPromptStyler.__name__ = node_name
    return CustomPromptStyler

styler_data = StylerData("data")
combo_config = load_combo_config()
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# Single-style nodes
for menu in styler_data.menus:
    node_name = f"{menu.capitalize()}Styler"
    cls = make_styler_node_class(node_name, [menu])
    NODE_CLASS_MAPPINGS[node_name] = cls
    display_name = f"{styler_data.get_menu_label(menu)} Styler"
    NODE_DISPLAY_NAME_MAPPINGS[node_name] = display_name

# Combo nodes from config
for combo_name, combo_menus in combo_config.items():
    node_name = combo_name.replace(" ", "").replace("+", "") + "Styler"
    cls = make_styler_node_class(node_name, combo_menus)
    NODE_CLASS_MAPPINGS[node_name] = cls
    NODE_DISPLAY_NAME_MAPPINGS[node_name] = f"{combo_name} Styler"

# Optional fallback combo node
if "Perfection beta Styler" not in NODE_DISPLAY_NAME_MAPPINGS:
    menus = ["filter_options", "unique_identifier", "subject_count", "Fashion", "era", "mode"]
    NODE_CLASS_MAPPINGS["PerfectionBetaStyler"] = make_styler_node_class("PerfectionBetaStyler", menus)
    NODE_DISPLAY_NAME_MAPPINGS["PerfectionBetaStyler"] = "Perfection beta Styler"
