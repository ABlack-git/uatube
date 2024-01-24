import re
import typing as t
from dataclasses import dataclass, field

from itemloaders.processors import TakeFirst, MapCompose, Identity
from scrapy.loader import ItemLoader


@dataclass
class ManifestChannel:
    rank: int = None
    channel_name: str = None
    channel_id: str = None
    channel_url: str = None

    num_subscribers: int = None
    num_views: int = None
    num_videos: int = None

    categories: t.List[str] = field(default_factory=list)


class ManifestChannelItemLoader(ItemLoader):
    default_item_class = ManifestChannel
    default_output_processor = TakeFirst()

    channel_id_in = MapCompose(lambda x: re.search(r'/(channel|user)/([^/]+)', x).group(2))
    channel_id_out = TakeFirst()
    categories_in = Identity()
    categories_out = Identity()

    rank_in = MapCompose(lambda x: int(x))
    num_subscribers_in = MapCompose(lambda x: int(x))
    num_views_in = MapCompose(lambda x: int(x))
    num_videos_in = MapCompose(lambda x: int(x))

