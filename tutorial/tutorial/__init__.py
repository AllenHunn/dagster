from dagster import Definitions, load_assets_from_modules
from .resources import DataGeneratorResource

from . import assets
from . import stories

all_assets = load_assets_from_modules([assets, stories])

defs = Definitions(
    assets=all_assets,
    resources={"hackernews_api": DataGeneratorResource()},
)
