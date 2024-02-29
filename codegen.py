import os
github_url_gicons = "https://github.com/google/material-design-icons"

gicons_tmp = "/tmp/google-icons-tmp"

# download icons
os.system(f"mkdir {gicons_tmp} && git clone --depth=1 --filter=blob:none --sparse {github_url_gicons} {gicons_tmp} && cd {gicons_tmp} && git sparse-checkout init --cone && git sparse-checkout set src")

def to_camel_case(snake_str: str) -> str:
    components = snake_str.split('_')
    return ''.join(x.title() for x in components)

def get_style(style: str) -> str:
    match style:
        case "materialiconsround":
            return "round"
        case "materialiconssharp":
            return "sharp"
        case "materialiconsoutlined":
            return "outlined"
        case "materialiconstwotone":
            return "twotone"
        case _:
            return "filled"

os.system("rm -rf ./src/icons/* && mkdir ./src/icons/components && mkdir ./src/icons/svg")

imports: dict[str, list[str]] = {}
variants: dict[str, list[str]] = {}
ts_filenames: list[str] = []

def gen_code():
    global imports, variants, ts_filenames
    for icon_name_short in imports:
        code = "import React from \"react\";\n"
        code += "\n".join(imports[icon_name_short]) + "\n\n"
        for variant in variants[icon_name_short]:
            size, style = variant.split("_")
            code += f"export const Icon{icon_name_short}{size}{style} = () => <SVG{icon_name_short}_{size}_{style} />;\n"
        with open("./src/icons/components/" + icon_name_short + ".tsx", "w") as f:
            f.write(code)
        ts_filenames.append("./" + icon_name_short)
    
    # create file ./src/icons/index.ts
    code = "export * from \"./components\";"
    with open("./src/icons/index.ts", "w") as f:
        f.write(code)
    
    # create file ./src/icons/components/index.ts
    code = "\n".join([f"export * from \"{filename}\";" for filename in ts_filenames])
    with open("./src/icons/components/index.ts", "w") as f:
        f.write(code)
    
    
        
        
        

for foldername, subfolders, filenames in os.walk(gicons_tmp + "/src"):

    for filename in filenames:
        file_path = os.path.join(foldername, filename)
        params = file_path.split("/")[4:]
        icon_name_short = to_camel_case(params[0] + "_" + params[1])
        size = int(params[3].split("px.svg")[0])
        style = get_style(params[2])
        print(f'{icon_name_short}: {params}')
        
        # create file /src/icons/svg/{icon_name_short}/{size}_{style}.svg
        if not os.path.exists(f"./src/icons/svg/{icon_name_short}"):
            os.makedirs(f"./src/icons/svg/{icon_name_short}")
        with open(file_path, "r") as original_svg:
            with open(f"./src/icons/svg/{icon_name_short}/{size}_{style}.svg", "w") as new_svg:
                new_svg.write(original_svg.read().replace("<svg", "<svg fill=\"currentColor\""))
        
        # create file /src/icons/components/{icon_name_short}.tsx
        if not os.path.exists(f"./src/icons/components"):
            os.makedirs(f"./src/icons/components/{icon_name_short}")
        if not os.path.exists(f"./src/icons/components/{icon_name_short}.tsx"):
            os.system(f"touch ./src/icons/components/{icon_name_short}.tsx")
        
        imports[icon_name_short] = imports.get(icon_name_short, []) + [f"import SVG{icon_name_short}_{size}_{style} from '../svg/{icon_name_short}/{size}_{style}.svg';"]
        variants[icon_name_short] = variants.get(icon_name_short, []) + [f"{size}_{style}"]
        # exit(0)
    if len(imports) > 20:
        gen_code()
        exit(0)
gen_code()