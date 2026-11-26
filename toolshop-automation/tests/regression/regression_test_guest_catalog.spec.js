import { test } from "@playwright/test";
import { CatalogPage } from "../../module_object/CatalogPage";
import { ProductPage } from "../../module_object/ProductPage";

test.describe("Catalog browsing", { tag: "@regression" }, () => {
  let category;

  test.beforeAll("Test data preparation", () => {
    category = "Hammer";
  });

  test("TC04 Sort by price low to high and verify prices are ascending", async ({ page }) => {
    const catalogPage = new CatalogPage(page);

    await catalogPage.open_catalog();
    await catalogPage.sort_products_by_price_low_to_high();
    await catalogPage.assert_product_prices_sorted_ascending();
  });

  test("TC05 Filter by a category and verify only that category is listed", async ({ page }) => {
    const catalogPage = new CatalogPage(page);

    await catalogPage.open_catalog();
    await catalogPage.filter_products_by_category(category);
    await catalogPage.assert_every_product_name_contains(category);
  });

  test("TC06 Open a product and verify its name and price match the catalog card", async ({ page }) => {
    const catalogPage = new CatalogPage(page);
    const productPage = new ProductPage(page);

    await catalogPage.open_catalog();
    const product = await catalogPage.get_first_product_card_details();
    await catalogPage.open_first_product();
    await productPage.assert_product_details(product.name, product.price);
  });
});
