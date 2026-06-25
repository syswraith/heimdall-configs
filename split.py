from pathlib import Path
import shutil
import yaml

CONFIG_FILE = Path("config.yaml")
SERVICES_FILE = Path(".services_added")

with CONFIG_FILE.open("r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

services_added = []

for service_entry in config.get("services", []):
    name, data = next(iter(service_entry.items()))

    services_added.append(name)

    category = data.get("category", "uncategorized")

    category_dir = Path(category)
    category_dir.mkdir(parents=True, exist_ok=True)

    output_file = category_dir / f"{name}.yaml"

    with output_file.open("w", encoding="utf-8") as f:
        yaml.safe_dump(
            data,
            f,
            sort_keys=False,
            default_flow_style=False,
            allow_unicode=True,
        )

CONFIG_FILE.unlink()

SERVICES_FILE.write_text(",".join(services_added), encoding="utf-8")
