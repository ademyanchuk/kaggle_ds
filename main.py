import argparse
import json
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi

API = KaggleApi()
API.authenticate()

PARSER = argparse.ArgumentParser("Kaggle api dataset from folder")
PARSER.add_argument("src", help="path to folder from which to create dataset")
branch = PARSER.add_mutually_exclusive_group(required=True)
branch.add_argument(
    "-c", "--create", action="store_true", help="use to initialize and create dataset"
)
branch.add_argument(
    "-u", "--update", action="store_true", help="use to update existing dataset"
)
PARSER.add_argument(
    "-m",
    "--message",
    default="Next update",
    help="message to add then updating dataset",
)


def init_ds(path: Path):
    assert path.exists() and path.is_dir()
    API.dataset_initialize(path)


def update_meta(path: Path):
    with open(path, "r") as fin:
        meta = json.load(fin)
    title = path.parent.name.replace("-", "_")
    meta["title"] = title

    id_name = title.replace("_", "-")
    split = meta["id"].split("/")
    id_name = "/".join([split[0], id_name])
    meta["id"] = id_name

    with open(path, "w") as fout:
        json.dump(meta, fout)


def main():
    args = PARSER.parse_args()
    path = Path(args.src)
    if args.create:
        init_ds(path)
        update_meta(path / "dataset-metadata.json")
        API.dataset_create_new_cli(path, convert_to_csv=False, dir_mode="zip")
    elif args.update:
        API.dataset_create_version_cli(
            path, version_notes=args.message, convert_to_csv=False, dir_mode="zip"
        )


if __name__ == "__main__":
    main()
