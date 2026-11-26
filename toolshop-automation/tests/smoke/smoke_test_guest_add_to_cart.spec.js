import { test } from "@playwright/test";
import { FlowShopping } from "../../flows/FlowShopping";
import { Header } from "../../module_object/Header";
import { CartPage } from "../../module_object/CartPage";

test.describe("Add to cart", { tag: "@smoke" }, () => {
  test("TC03 Add a product with quantity 2 and verify the badge and cart row", async ({ page }) => {
    const flowShopping = new FlowShopping(page);
    const header = new Header(page);
    const cartPage = new CartPage(page);

    const product = await flowShopping.add_first_catalog_product_to_cart(2);
    await header.open_cart();
    await cartPage.assert_product_in_cart(product.name, 2);
  });
});
