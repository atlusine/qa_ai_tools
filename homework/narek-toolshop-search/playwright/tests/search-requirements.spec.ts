import { test, expect } from '@playwright/test';
import { openHome, search, shownNames, expectedFor, PLIERS } from './search-helpers';

// SCRUM-7 requirement-based cases. Docs: ../../test-cases/01-test-cases-requirements.md
test.describe('SCRUM-7 search: requirements', () => {
  test.beforeEach(async ({ page }) => openHome(page));

  test('SRCH-001 search controls are shown on home page', async ({ page }) => {
    for (const id of ['search-query', 'search-submit', 'search-reset']) {
      await expect(page.getByTestId(id)).toBeVisible();
      await expect(page.getByTestId(id)).toBeEnabled();
    }
  });

  test('SRCH-002 "pliers" shows exactly the 4 pliers', async ({ page }) => {
    await search(page, 'pliers');
    expect(await shownNames(page)).toEqual(PLIERS);
  });

  test('SRCH-003 caption "Searched for: pliers"', async ({ page }) => {
    await search(page, 'pliers');
    await expect(page.getByTestId('search-caption')).toHaveText('Searched for: pliers');
  });

  for (const [id, term] of [['SRCH-004', 'PLIERS'], ['SRCH-005', 'plier'], ['SRCH-006', 'pLiErS'], ['SRCH-007', 'lier']]) {
    test(`${id} "${term}" shows the same 4 pliers`, async ({ page }) => {
      await search(page, term);
      expect(await shownNames(page)).toEqual(PLIERS);
    });
  }

  for (const [id, term] of [['SRCH-008', 'hammer'], ['SRCH-009', 'ham']]) {
    test(`${id} "${term}" matches the catalogue`, async ({ page, request }) => {
      await search(page, term);
      expect(await shownNames(page)).toEqual(await expectedFor(request, term));
    });
  }

  test('SRCH-010 second search replaces the first', async ({ page, request }) => {
    await search(page, 'pliers');
    await search(page, 'hammer');
    await expect(page.getByTestId('search-caption')).toHaveText('Searched for: hammer');
    expect(await shownNames(page)).toEqual(await expectedFor(request, 'hammer'));
  });

  test('SRCH-011 caption shows text exactly as typed', async ({ page }) => {
    await search(page, 'PLIERS');
    await expect(page.getByTestId('search-caption')).toHaveText('Searched for: PLIERS');
  });

  test('SRCH-012 X restores the full list after a search', async ({ page }) => {
    const initial = await shownNames(page);
    await search(page, 'pliers');
    await page.getByTestId('search-reset').click();
    await expect(page.getByTestId('search-query')).toHaveValue('');
    await expect(page.getByTestId('search-caption')).toHaveCount(0);
    await expect.poll(() => shownNames(page)).toEqual(initial);
  });

  test.fixme('SRCH-013 search works when logged in (manual: needs Narek to sign in)', async () => {});

  test('SRCH-014 no-results message for "xyzxyz"', async ({ page }) => {
    await search(page, 'xyzxyz');
    await expect(page.getByText('There are no products found.')).toBeVisible();
  });

  test('SRCH-015 no product cards for "xyzxyz"', async ({ page }) => {
    await search(page, 'xyzxyz');
    await expect(page.getByTestId('product-name')).toHaveCount(0);
  });

  test('SRCH-016 X restores full list after no-results', async ({ page }) => {
    const initial = await shownNames(page);
    await search(page, 'xyzxyz');
    await page.getByTestId('search-reset').click();
    await expect(page.getByTestId('search-query')).toHaveValue('');
    await expect(page.getByText('There are no products found.')).toHaveCount(0);
    await expect.poll(() => shownNames(page)).toEqual(initial);
  });

  test('SRCH-017 "pliers!" shows no results', async ({ page }) => {
    await search(page, 'pliers!');
    await expect(page.getByText('There are no products found.')).toBeVisible();
    await expect(page.getByTestId('product-name')).toHaveCount(0);
  });
});
