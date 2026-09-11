import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.cronista_service import CronistaService


class TestCronistaService(unittest.TestCase):
    def setUp(self):
        self.service = CronistaService()

    def test_list_articles(self):
        articles = self.service.list_articles(limit=5)
        self.assertIsInstance(articles, list)
        if articles:
            first = articles[0]
            self.assertTrue(len(first.title) > 0)
            self.assertTrue(len(first.slug) > 0)
            self.assertIsNotNone(first.reading_time)

    def test_get_article_detail(self):
        articles = self.service.list_articles(limit=1)
        if articles:
            slug = articles[0].slug
            detail = self.service.get_article(slug)
            self.assertIsNotNone(detail)
            self.assertEqual(detail.slug, slug)
            self.assertIn("content_markdown", detail.__dict__)
            self.assertTrue(len(detail.content_markdown) > 0)

    def test_get_nonexistent_article(self):
        detail = self.service.get_article("slug-inexistente-12345")
        self.assertIsNil = self.assertIsNone(detail)


if __name__ == "__main__":
    unittest.main()
