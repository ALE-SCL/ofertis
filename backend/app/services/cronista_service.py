import os
import glob
import logging
from typing import List, Optional, Dict, Any
try:
    from pydantic import BaseModel
except ImportError:
    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
        def dict(self):
            return self.__dict__
        def model_dump(self):
            return self.__dict__

logger = logging.getLogger("ofertis.cronista_service")


class CronistaArticleSummary(BaseModel):
    slug: str
    title: str
    subtitle: Optional[str] = None
    date: Optional[str] = None
    reading_time: Optional[str] = None
    bulletin_source: Optional[str] = None
    tags: List[str] = []
    summary: Optional[str] = None


class CronistaArticleDetail(CronistaArticleSummary):
    content_markdown: str


class CronistaService:
    def __init__(self):
        self.articles_dir = self._find_articles_dir()

    def _find_articles_dir(self) -> str:
        candidates = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "cronista", "articles"),
            "/app/cronista/articles",
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cronista_articles"),
        ]
        for c in candidates:
            if os.path.exists(c) and os.path.isdir(c):
                return c
        return candidates[0]

    def _parse_frontmatter(self, raw_content: str) -> tuple[Dict[str, Any], str]:
        """Extrae metadata YAML del frontmatter y el contenido markdown."""
        metadata: Dict[str, Any] = {}
        markdown_body = raw_content

        if raw_content.startswith("---"):
            parts = raw_content.split("---", 2)
            if len(parts) >= 3:
                frontmatter_text = parts[1]
                markdown_body = parts[2].strip()

                for line in frontmatter_text.strip().split("\n"):
                    if ":" in line:
                        key, val = line.split(":", 1)
                        key = key.strip()
                        val = val.strip().strip('"').strip("'")
                        if key == "tags":
                            try:
                                import ast
                                metadata["tags"] = ast.literal_eval(val)
                            except Exception:
                                metadata["tags"] = [t.strip() for t in val.strip("[]").split(",") if t.strip()]
                        else:
                            metadata[key] = val

        return metadata, markdown_body

    def list_articles(self, limit: int = 20) -> List[CronistaArticleSummary]:
        if not os.path.exists(self.articles_dir):
            return []

        md_files = glob.glob(os.path.join(self.articles_dir, "*.md"))
        md_files.sort(key=os.path.getmtime, reverse=True)

        summaries: List[CronistaArticleSummary] = []
        for fpath in md_files[:limit]:
            slug = os.path.splitext(os.path.basename(fpath))[0]
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()

                meta, body = self._parse_frontmatter(content)
                lead = meta.get("subtitle")
                if not lead:
                    for line in body.split("\n"):
                        stripped = line.strip()
                        if stripped and not stripped.startswith("#") and not stripped.startswith(">"):
                            lead = stripped[:200] + "..."
                            break

                summaries.append(
                    CronistaArticleSummary(
                        slug=slug,
                        title=meta.get("title", slug.replace("-", " ").title()),
                        subtitle=meta.get("subtitle"),
                        date=meta.get("date"),
                        reading_time=meta.get("reading_time", "4 min"),
                        bulletin_source=meta.get("bulletin_source"),
                        tags=meta.get("tags", []),
                        summary=lead
                    )
                )
            except Exception as e:
                logger.error(f"Error parseando artículo {fpath}: {e}")

        return summaries

    def get_article(self, slug: str) -> Optional[CronistaArticleDetail]:
        if not os.path.exists(self.articles_dir):
            return None

        clean_slug = os.path.basename(slug).replace(".md", "")
        fpath = os.path.join(self.articles_dir, f"{clean_slug}.md")
        if not os.path.exists(fpath):
            return None

        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()

            meta, body = self._parse_frontmatter(content)
            return CronistaArticleDetail(
                slug=clean_slug,
                title=meta.get("title", clean_slug.replace("-", " ").title()),
                subtitle=meta.get("subtitle"),
                date=meta.get("date"),
                reading_time=meta.get("reading_time", "4 min"),
                bulletin_source=meta.get("bulletin_source"),
                tags=meta.get("tags", []),
                summary=meta.get("subtitle"),
                content_markdown=body
            )
        except Exception as e:
            logger.error(f"Error leyendo detalle de artículo {fpath}: {e}")
            return None
