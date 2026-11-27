import { test, expect, type Page } from '@playwright/test';
import { openHome, search, shownNames, expectedFor, PLIERS, API } from './search-helpers';

// Extended / self-monitoring cases. Docs: ../../test-cases/03-test-cases-extended.md
const caption = (page: Page) => page.getByTestId('search-caption');
const noResults = (page: Page) => page.getByText('There are no products found.');

test.describe('SCRUM-7 search: extended', () => {
  test.beforeEach(async ({ page }) => openHome(page));

  // 1. How the user submits
  test('EX-01 Enter submits the search', async ({ page }) => {
    await search(page, 'pliers', 'enter');
    await expect(caption(page)).toHaveText('Searched for: pliers');
    expect(await shownNames(page)).toEqual(PLIERS);
  });

  test('EX-02 typing letter by letter', async ({ page }) => {
    await page.getByTestId('search-query').pressSequentially('pliers', { delay: 80 });
    const resp = page.waitForResponse(r => r.url().includes('/products/search'));
    await page.getByTestId('search-submit').click();
    await resp;
    await expect(caption(page)).toHaveText('Searched for: pliers');
    await expect.poll(() => shownNames(page)).toEqual(PLIERS);
    expect(await shownNames(page)).toEqual(PLIERS);
  });

  test('EX-03 keyboard only', async ({ page }) => {
    await page.getByTestId('search-query').focus();
    await page.keyboard.type('pliers');
    for (let i = 0; i < 4; i++) {
      await page.keyboard.press('Tab');
      if (await page.getByTestId('search-submit').evaluate(el => el === document.activeElement)) break;
    }
    await expect(page.getByTestId('search-submit')).toBeFocused();
    const resp = page.waitForResponse(r => r.url().includes('/products/search'));
    await page.keyboard.press('Enter');
    await resp;
    await expect(caption(page)).toHaveText('Searched for: pliers');
    await expect.poll(() => shownNames(page)).toEqual(PLIERS);
  });

  test('EX-04 double-click Search shows each product once', async ({ page }) => {
    await page.getByTestId('search-query').fill('pliers');
    await page.getByTestId('search-submit').dblclick();
    await expect(caption(page)).toHaveText('Searched for: pliers');
    await page.waitForTimeout(1500);
    expect(await shownNames(page)).toEqual(PLIERS);
  });

  test('EX-05 last of 5 rapid searches wins', async ({ page }) => {
    for (const t of ['saw', 'drill', 'hammer', 'wrench', 'pliers']) {
      await page.getByTestId('search-query').fill(t);
      await page.getByTestId('search-submit').click();
    }
    await page.waitForTimeout(3000);
    await expect(caption(page)).toHaveText('Searched for: pliers');
    expect(await shownNames(page)).toEqual(PLIERS);
  });

  test('EX-06 one click sends exactly one request', async ({ page }) => {
    let n = 0;
    page.on('request', r => { if (r.url().includes('/products/search')) n++; });
    await search(page, 'pliers');
    await page.waitForTimeout(1500);
    expect(n).toBe(1);
  });

  // 2. Length boundaries
  for (const [id, term] of [['EX-07', 'p'], ['EX-08', 'pl'], ['EX-09', 'pli']]) {
    test(`${id} ${term.length}-char term "${term}" is searched`, async ({ page, request }) => {
      const resp = await search(page, term);
      expect(resp, 'a search request should be sent').not.toBeNull();
      await expect(caption(page)).toHaveText(`Searched for: ${term}`);
      // UI shows max 9 per page, so compare the first page against the oracle
      const exp = await expectedFor(request, term);
      const shown = await shownNames(page);
      expect(shown.every(n => exp.includes(n)), `shown ${shown} must contain "${term}"`).toBe(true);
    });
  }

  for (const [id, len] of [['EX-10', 40], ['EX-11', 41]] as const) {
    test(`${id} ${len}-char term is searched`, async ({ page }) => {
      const term = 'a'.repeat(len);
      const resp = await search(page, term);
      expect(resp, 'a search request should be sent (or a length message shown)').not.toBeNull();
      await expect(caption(page)).toHaveText(`Searched for: ${term}`);
      await expect(noResults(page)).toBeVisible();
    });
  }

  // 3. Spaces and empty input
  for (const [id, term] of [['EX-12', ''], ['EX-13', '   ']]) {
    test(`${id} ${term ? 'whitespace-only' : 'empty'} search keeps full list`, async ({ page }) => {
      const initial = await shownNames(page);
      await search(page, term);
      await expect(caption(page)).toHaveCount(0);
      await expect(noResults(page)).toHaveCount(0);
      expect(await shownNames(page)).toEqual(initial);
    });
  }

  test('EX-14 leading/trailing spaces are trimmed', async ({ page }) => {
    await search(page, '  pliers  ');
    expect(await shownNames(page)).toEqual(PLIERS);
  });

  test('EX-15 field keeps the term after searching', async ({ page }) => {
    await search(page, 'pliers');
    await expect(page.getByTestId('search-query')).toHaveValue('pliers');
  });

  // 4. Product-name shapes
  for (const [id, term] of [['EX-16', 'long nose'], ['EX-17', 'flat-head'], ['EX-18', '24v'], ['EX-19', '(set)'], ['EX-20', '7.5m'], ['EX-21', 'ammer'], ['EX-22', 'pliers long']]) {
    test(`${id} "${term}" matches the catalogue`, async ({ page, request }) => {
      await search(page, term);
      expect(await shownNames(page)).toEqual(await expectedFor(request, term));
    });
  }

  // 5. Special characters and security
  // 3+ characters, because 1-2 characters are never searched (SCRUM-10, EX-07/08)
  const special: [string, string][] = [
    ['EX-23', '%%%'], ['EX-24', 'pl_ers'], ['EX-25', "' OR '1'='1"], ['EX-26', '<script>alert(1)</script>'],
    ['EX-27', '<b>pliers</b>'], ['EX-28a', '\\\\\\'], ['EX-28b', '"""'], ['EX-29', '*pliers*'], ['EX-30a', '🔨🔨🔨'], ['EX-30b', 'Плоскогубцы'],
  ];
  for (const [id, term] of special) {
    test(`${id} special input ${JSON.stringify(term)}`, async ({ page, request }) => {
      let dialog = false;
      page.on('dialog', d => { dialog = true; d.dismiss(); });
      const resp = await search(page, term);
      expect(dialog, 'no script may run').toBe(false);
      if (resp) expect(resp.status(), 'no server error').toBeLessThan(500);
      await expect(caption(page)).toHaveText(`Searched for: ${term}`);
      await expect(page.locator('[data-test=search-caption] b, [data-test=search-caption] script')).toHaveCount(0);
      expect(await shownNames(page)).toEqual(await expectedFor(request, term));
    });
  }

  // 6. Search combined with other actions
  test('EX-31 sorting keeps the search', async ({ page, request }) => {
    await search(page, 'hammer');
    await page.getByTestId('sort').selectOption({ label: 'Price (High - Low)' });
    await page.waitForTimeout(2500);
    const names = await page.getByTestId('product-name').allTextContents();
    const prices = (await page.getByTestId('product-price').allTextContents()).map(p => parseFloat(p.replace(/[^0-9.]/g, '')));
    expect(names.every(n => /hammer/i.test(n)), `only hammers, got ${names}`).toBe(true);
    expect(prices).toEqual([...prices].sort((a, b) => b - a));
    expect(names.length).toBeGreaterThan(0);
  });

  test('EX-32 category filter narrows the search', async ({ page }) => {
    await search(page, 'claw');
    await page.getByLabel('Hammer', { exact: true }).check();
    await page.waitForTimeout(2500);
    const names = await page.getByTestId('product-name').allTextContents();
    expect(names.length).toBeGreaterThan(0);
    expect(names.every(n => /claw/i.test(n) && /hammer/i.test(n)), `got ${names}`).toBe(true);
  });

  test('EX-33 results survive product page and Back', async ({ page }) => {
    await search(page, 'pliers');
    await page.getByTestId('product-name').first().click();
    await expect(page).toHaveURL(/\/product\//);
    await page.goBack();
    await page.waitForTimeout(2500);
    await expect(caption(page)).toHaveText('Searched for: pliers');
    expect(await shownNames(page)).toEqual(PLIERS);
  });

  test('EX-34 search in German UI', async ({ page }) => {
    await page.getByTestId('language-select').click();
    await page.getByTestId('lang-de').click();
    await page.waitForTimeout(1500);
    await search(page, 'pliers');
    expect(await shownNames(page)).toEqual(PLIERS);
  });

  // 7. Server and network problems
  test('EX-36 server error is shown as an error', async ({ page }) => {
    await page.route('**/products/search**', r => r.fulfill({ status: 500, contentType: 'application/json', body: '{"message":"Server Error"}' }));
    await search(page, 'pliers');
    await page.waitForTimeout(1000);
    await expect(noResults(page), 'a 500 must not look like "no products"').toHaveCount(0);
    await expect(page.getByText(/error|went wrong|try again|unavailable/i).first()).toBeVisible();
  });

  test('EX-37 network failure is shown as an error', async ({ page }) => {
    await page.route('**/products/search**', r => r.abort('failed'));
    await search(page, 'pliers');
    await page.waitForTimeout(1000);
    await expect(noResults(page), 'a failed request must not look like "no products"').toHaveCount(0);
    await expect(page.getByText(/error|went wrong|try again|offline|connection/i).first()).toBeVisible();
  });

  // 8. Monitoring
  test('EX-38 30 common terms match the live catalogue', async ({ page, request }) => {
    test.setTimeout(180_000);
    const terms = ['saw', 'drill', 'screw', 'wrench', 'tape', 'glove', 'helmet', 'sander', 'cutter', 'nut', 'bolt', 'chisel', 'hammer', 'pliers', 'measure',
      'cordless', 'wood', 'claw', 'thor', 'spanner', 'belt', 'cabinet', 'goggles', 'ear', 'protection', 'driver', 'grip', 'handle', 'set', 'head'];
    const mismatches: string[] = [];
    for (const t of terms) {
      await search(page, t);
      const exp = await expectedFor(request, t);
      const shown = await shownNames(page);
      const want = exp.length > 9 ? null : exp; // grid shows max 9; only compare full sets
      if (want ? JSON.stringify(shown) !== JSON.stringify(want) : !shown.every(n => exp.includes(n)))
        mismatches.push(`${t}: missing [${exp.filter(n => !shown.includes(n)).join(', ')}] extra [${shown.filter(n => !exp.includes(n)).join(', ')}]`);
    }
    expect(mismatches, mismatches.join('\n')).toEqual([]);
  });

  test('EX-39 AC terms are stable over 5 repeats (API)', async ({ request }) => {
    const problems: string[] = [];
    for (let i = 1; i <= 5; i++) {
      for (const t of ['pliers', 'PLIERS', 'plier']) {
        const r = await request.get(`${API}/products/search?q=${encodeURIComponent(t)}`);
        const names = r.ok() ? (await r.json()).data.map((p: { name: string }) => p.name).sort() : [];
        if (r.status() !== 200 || JSON.stringify(names) !== JSON.stringify(PLIERS)) problems.push(`#${i} ${t}: HTTP ${r.status()}, ${names.length} results`);
      }
    }
    expect(problems, problems.join('\n')).toEqual([]);
  });
});

test.describe('SCRUM-7 search: mobile', () => {
  test.use({ viewport: { width: 375, height: 812 }, isMobile: true, hasTouch: true });
  test('EX-35 search on a phone screen', async ({ page }) => {
    await openHome(page);
    const box = page.getByTestId('search-query');
    if (!(await box.isVisible())) await page.getByRole('button', { name: /filters/i }).click();
    await expect(box).toBeVisible();
    await search(page, 'pliers');
    expect(await shownNames(page)).toEqual(PLIERS);
  });
});
