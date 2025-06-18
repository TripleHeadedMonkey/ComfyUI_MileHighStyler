https://youtu.be/WBHI-2uww7o?si=dijvDaUI4nmx4VkF

Absolutely! Here’s a **clear, user-friendly README.md** for your `MileHighStyler` node package.

---

# MileHighStyler for ComfyUI

**MileHighStyler** is a highly flexible custom node for [ComfyUI](https://github.com/comfyanonymous/ComfyUI) that lets you combine powerful style templates with your own prompt—using precise control over placement, weighting, and offsets.

* **Custom styles?** Easily extendable.
* **Stackable?** Yes, endlessly.
* **Offset prompt position?** Yes, to any spot in the template.
* **Advanced combo menus?** Yes, supports multi-menu combos!

---

## Features

* **Per-style weighting** (e.g., apply styles at strengths like `("my style":2.0)`).
* **Per-style offset:** Place your prompt *anywhere* in the template, not just where `{prompt}` appears.
* **Multiple style menus:** Organize your templates by category.
* **Combined/combo menus:** Mix and match categories (like “Fashion + Era + Mode”) in one node.
* **Negative prompt support.**
* **Stack nodes for complex, layered effects.**

---

## Installation

1. **Download or clone this repo** into your ComfyUI custom nodes directory:

   ```
   ComfyUI/custom_nodes/MileHighStyler/
   ```

2. Ensure your folder has this structure:

   ```
   MileHighStyler/
     ├── sdxl_prompt_styler.py
     ├── data/
     │    └── [menu folders...]
     └── styler_config.json
   ```

3. **Restart ComfyUI.**
   Nodes will appear under the "MileHighStyler" category.

---

## Basic Usage

1. **Add the desired MileHighStyler node** (e.g., `Perfection beta Styler`, `FashionStyler`, or your combo node).
2. **Enter your prompt** in the `text_positive` field.
3. (Optional) Enter a negative prompt.
4. **Select styles** from the dropdowns for each menu item.
5. **Adjust the style weight** (default is `2.0`, but any value between 1 and 3 is allowed).
6. **Adjust the offset** (see "Prompt Offset" below).
7. **Connect output** to your workflow.

### Prompt Offset

* **0** (default): places your prompt exactly where `{prompt}` is in the template JSON.
* **Positive values:** inserts your prompt after Nth word (from the start) in the style.
* **Negative values:** inserts your prompt before Nth word from the end of the style.
* `{prompt}` is always removed from the output.

---

## How to Add Custom Styles

**To add a new style menu:**

1. **Create a new folder** under `data/` named for your menu, e.g., `data/ArtMovement`.

2. **Add one or more JSON files** to this folder. Each file should be a list of style entries, e.g.:

   ```json
   [
     {
       "name": "Impressionism",
       "prompt": "impressionist art, {prompt}, vibrant brushstrokes",
       "negative_prompt": "blurry, washed out"
     },
     {
       "name": "Cubism",
       "prompt": "cubist shapes, {prompt}, geometric abstraction",
       "negative_prompt": ""
     }
   ]
   ```

* **`name`**: What shows up in the node dropdown.
* **`prompt`**: Must include `{prompt}` where you want the user’s input (or omit it if you’ll always use offsets).
* **`negative_prompt`**: (optional) Anything to append to the negative prompt.

**To add a new style entry to an existing menu:**

* Just add another object in the menu’s JSON file(s).

---

## How to Add Menu Items to the Big Menus (Combo Nodes)

1. **Edit `styler_config.json`** in the main `MileHighStyler` folder.
2. **Add or change combo menu definitions.**
   Example:

   ```json
   {
     "Perfection beta": ["filter_options", "unique_identifier", "subject_count", "Fashion", "era", "mode"],
     "Art Fusion": ["ArtMovement", "ColorPalette", "Lighting"]
   }
   ```

* The **keys** become the names of the combo nodes.
* The **values** are lists of menu folder names (must match folders in `data/`).
* Each combo menu will have an individual weight and offset per menu field.

3. **Restart ComfyUI** to see the new combo nodes.

---

## Advanced: Menu Labels

* You can use a `menu_labels.json` file in your `data/` directory to customize how menu names appear in the UI.

Example `menu_labels.json`:

```json
{
  "Fashion": "Fashion Style",
  "era": "Time Period",
  "mode": "Rendering Mode"
}
```

---

## How the Code Works

* **Templates:** Each style entry in your JSON is turned into a `Template` object with a `prompt` and (optionally) a `negative_prompt`.

* **StylerData:** Loads all menu folders and entries into memory at startup.

* **Dynamic Node Generation:** For each menu and each combo (from `styler_config.json`), a unique node class is created at runtime with per-menu fields.

* **Prompt Replacement:**

  * If offset is **0**, the user’s prompt replaces the first `{prompt}` found in the style template.
  * If offset is **positive**, the prompt is inserted after N words (from the start); any `{prompt}` is removed.
  * If offset is **negative**, the prompt is inserted before N words from the end; any `{prompt}` is removed.

* **Weighting:**
  Everything except the user prompt is wrapped in `("...":style_weight)`, so your style is weighted but the actual prompt isn’t.

* **Stacking:**
  You can feed one styler node’s output into another to layer multiple style effects.

### For Customization

* To **add logic** (e.g., support for multi-line prompts, extra fields), modify the `Template.replace_prompts` method.
* To **change menu organization or UI**, edit `make_styler_node_class` or add new menus/combo logic.
* All configuration is **data-driven**—no code changes needed for new styles or menu structures!
* The code is written to be readable and modular—check out `sdxl_prompt_styler.py` to see exactly how everything ties together.

---

## Need Help?

Open an issue or discussion on the repo!
Contributions, ideas, and custom style packs are very welcome.

---

**Happy styling!**
