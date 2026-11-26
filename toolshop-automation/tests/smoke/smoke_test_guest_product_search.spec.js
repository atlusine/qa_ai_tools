import { test } from "@playwright/test";
import { CatalogPage } from "../../module_object/CatalogPage";

test.describe("Product search", { tag: "@smoke" }, () => {
  let searchTerm;

  test.beforeAll("Test data preparation", () => {
    searchTerm = "pliers";
  });

  test("TC02 Search for a keyword and verify every result matches it", async ({ page }) => {
    const catalogPage = new CatalogPage(page);

    await catalogPage.open_catalog();
    await catalogPage.search_for_product(searchTerm);
    await catalogPage.assert_search_caption(searchTerm);
    await catalogPage.assert_every_product_name_contains(searchTerm);
  });
});
