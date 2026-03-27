#!/usr/bin/env -S uv run --quiet
# /// script
# dependencies = [
#   "md-template[natsort]>=0.2.1",
# ]
# ///

try:
    from mdtemplate.table.presets.scoop import ScoopTableTemplate
except ImportError:
    raise ImportError("Please install md-template: pip install md-template[natsort]")

if __name__ == "__main__":
    ScoopTableTemplate().parse_args().render()
