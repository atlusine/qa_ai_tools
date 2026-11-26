import { test } from "@playwright/test";
import { FlowShopping } from "../../flows/FlowShopping";
import { Header } from "../../module_object/Header";
import { CartPage } from "../../module_object/CartPage";
import { ProductPage } from "../../module_object/ProductPage";

test.describe("Cart management", { tag: "@regression" }, () => {
  let updatedQuantity;

  test.beforeAll("Test data preparation", () => {
    updatedQuantity = 3;
  });

  test("TC09 Change a cart quantity and verify the line price and total update", async ({ page }) => {
    const flowShopping = new FlowShopping(page);
    const header = new Header(page);
    const cartPage = new CartPage(page);
    const productPage = new ProductPage(page);

    const product = await flowShopping.add_first_catalog_product_to_cart();
    const unitPrice = await productPage.get_product_unit_price();
    await header.open_cart();
    await cartPage.update_product_quantity(product.name, updatedQuantity);
    await cartPage.assert_line_price_and_total(product.name, unitPrice, updatedQuantity);
  });

  test("TC10 Remove the only product and verify the cart is empty", async ({ page }) => {
    const flowShopping = new FlowShopping(page);
    const header = new Header(page);
    const cartPage = new CartPage(page);

    const product = await flowShopping.add_first_catalog_product_to_cart();
    await header.open_cart();
    await cartPage.remove_product(product.name);
    await cartPage.assert_cart_is_empty(product.name);
  });
});
