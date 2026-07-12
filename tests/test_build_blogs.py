import json
import unittest

from build_blogs import extract_faq_schema, normalize_public_content


class NormalizePublicContentTests(unittest.TestCase):
    def test_removes_unsupported_precision_from_rendered_copy(self):
        source = "<p>ช่วยกำจัดเชื้อได้ 99.9% ในพื้นที่สัมผัส</p>"

        result = normalize_public_content(source)

        self.assertNotIn("99.9%", result)
        self.assertIn("ดูแลความสะอาดตามขอบเขตงาน", result)

    def test_adds_dimensions_and_keeps_one_page_h1(self):
        source = '<h1>หัวข้อในเนื้อหา</h1><img src="cover.jpg" alt="ภาพปก">'

        result = normalize_public_content(source)

        self.assertNotIn("<h1", result)
        self.assertIn("<h2", result)
        self.assertIn('width="1200"', result)
        self.assertIn('height="675"', result)

    def test_returns_a_valid_graph_entry_when_an_article_has_no_faq(self):
        schema = extract_faq_schema("<p>เนื้อหาบทความทั่วไป</p>")

        self.assertEqual(json.loads(schema), {"@type": "WebPage"})


if __name__ == "__main__":
    unittest.main()
