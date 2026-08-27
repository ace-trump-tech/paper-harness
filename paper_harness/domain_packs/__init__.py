from .arts import ARTS
from .base import DomainPack
from .humanities import HUMANITIES
from .stem import STEM

PACKS = {pack.name: pack for pack in (STEM, HUMANITIES, ARTS)}

