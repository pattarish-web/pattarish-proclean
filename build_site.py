"""Run all site build steps."""

import build_blogs
import build_local_pages
import update_sitemap


def build_all():
    build_blogs.build_blogs()
    build_local_pages.build_local_pages()
    update_sitemap.update_sitemap()
    print("Site build complete.")


if __name__ == "__main__":
    build_all()
