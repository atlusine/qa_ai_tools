import { expect, type Page, type APIRequestContext } from '@playwright/test';

export const HOME = 'https://practicesoftwaretesting.com/';
export const API = 'https://api.practicesoftwaretesting.com';
export const PLIERS = ['Combination Pliers', 'Long Nose Pliers', 'Pliers', 'Slip Joint Pliers'];

/** Product names currently shown in the grid, trimmed and sorted. */
export async function shownNames(page: Page): Promise<string[]> {
  return (await page.getByTestId('product-name').allTextContents()).map(s => s.trim()).sort();
}

/** Open home and wait until the first product card is visible. */
export async function openHome(page: Page) {
  await page.goto(HOME);
  await expect(page.getByTestId('product-name').first()).toBeVisible();
}

/** Fill the search box and click Search. Waits for the search response if one is sent. */
export async function search(page: Page, text: string, submit: 'click' | 'enter' = 'click') {
  await page.getByTestId('search-query').fill(text);
  const resp = page.waitForResponse(r => r.url().includes('/products/search'), { timeout: 5000 }).catch(() => null);
  if (submit === 'click') await page.getByTestId('search-submit').click();
  else await page.getByTestId('search-query').press('Enter');
  const r = await resp;
  // let Angular render the response
  await page.waitForTimeout(400);
  return r; // null = no request was sent
}

/** Every product in the live catalogue (all pages), used as the test oracle. */
let catalogue: string[] | null = null;
export async function allProductNames(request: APIRequestContext): Promise<string[]> {
  if (catalogue) return catalogue;
  const names: string[] = [];
  for (let page = 1; ; page++) {
    const d = await (await request.get(`${API}/products?page=${page}`)).json();
    names.push(...d.data.map((p: { name: string }) => p.name));
    if (page >= d.last_page) break;
  }
  catalogue = names;
  return names;
}

/** Expected result per FR-02/FR-03: names that contain the text, case-insensitive. */
export async function expectedFor(request: APIRequestContext, text: string): Promise<string[]> {
  const t = text.toLowerCase();
  return (await allProductNames(request)).filter(n => n.toLowerCase().includes(t)).sort();
}
