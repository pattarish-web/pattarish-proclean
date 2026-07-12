import test from 'node:test';
import assert from 'node:assert/strict';

import { visibleText } from './seo_quality_utils.mjs';

test('visibleText excludes style and script content from marketing claims', () => {
  const html = '<style>.panel{width:100%}</style><script>const ratio="100%";</script><p>ตรวจงานตามขอบเขต</p>';

  assert.equal(visibleText(html), 'ตรวจงานตามขอบเขต');
});
