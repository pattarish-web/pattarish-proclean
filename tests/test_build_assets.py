import unittest

from build_assets import upgrade_public_html


class UpgradePublicHtmlTests(unittest.TestCase):
    def test_replaces_unsafe_geo_markup_with_complete_social_and_entity_markup(self):
        source = """<!doctype html><html lang=\"th\"><head>
        <title>บริการทดสอบ</title><meta name=\"description\" content=\"คำอธิบาย\">
        <link rel=\"canonical\" href=\"https://www.sangkanclean.com/example.html\">
        <meta name=\"geo.position\" content=\"13.7;100.5\">
        <script type=\"application/ld+json\">{\"@type\":\"LocalBusiness\",\"geo\":{\"@type\":\"GeoCoordinates\"}}</script>
        </head><body><h1>บริการทดสอบ</h1><img src=\"cover.jpg\" alt=\"ภาพบริการ\"></body></html>"""

        result = upgrade_public_html(source, "example.html")

        self.assertNotIn("geo.position", result)
        self.assertNotIn("GeoCoordinates", result)
        self.assertIn('property="og:title"', result)
        self.assertIn('name="twitter:card"', result)
        self.assertIn('https://www.sangkanclean.com/#organization', result)
        self.assertIn('width="1200"', result)
        self.assertIn('height="675"', result)

    def test_is_idempotent_when_the_site_is_rebuilt(self):
        source = """<html><head><title>หน้าเดิม</title><meta name=\"description\" content=\"คำอธิบาย\"><link rel=\"canonical\" href=\"https://www.sangkanclean.com/page.html\"></head><body><h1>หน้าเดิม</h1></body></html>"""

        once = upgrade_public_html(source, "page.html")
        twice = upgrade_public_html(once, "page.html")

        self.assertEqual(twice.lower().count('type="application/ld+json"'), 1)


if __name__ == "__main__":
    unittest.main()
