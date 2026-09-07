from app.scrapers.base_scraper import BaseScraperAdapter, RawScrapedProduct
from app.scrapers.cencosud_scraper import CencosudScraperAdapter
from app.scrapers.unimarc_scraper import UnimarcScraperAdapter
from app.scrapers.lider_scraper import LiderScraperAdapter

__all__ = [
    "BaseScraperAdapter",
    "RawScrapedProduct",
    "CencosudScraperAdapter",
    "UnimarcScraperAdapter",
    "LiderScraperAdapter",
]
