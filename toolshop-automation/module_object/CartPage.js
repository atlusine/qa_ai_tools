import { expect } from "@playwright/test";
import { SELECTORS } from "../support/selectors";
import { alertMessages } from "../support/messages";
import { PlaywrightMethods } from "../support/PlaywrightMethods";

export class CartPage {
  constructor(page) {
    this.page = page;
  }

  format_price(amount) {
    return `$${amount.toFixed(2)}`;
  }

  get_cart_row(productName) {
    return PlaywrightMethods.get_element(this.page, SELECTORS.cartRow).filter({ has: PlaywrightMethods.get_element(this.page, SELECTORS.cartRowProductTitle).filter({ hasText: productName }) });
  }

  async update_product_quantity(productName, quantity) {
    const updateCall = PlaywrightMethods.capture_api_call(this.page, "PUT", "/carts/*/product/quantity");
    const input = PlaywrightMethods.get_element(this.get_cart_row(productName), SELECTORS.cartRowQuantityInput);
    await input.fill(String(quantity));
    await input.press("Tab");
    await PlaywrightMethods.wait_api_call_and_assert_success_status(updateCall);
    await PlaywrightMethods.assert_toast_message(this.page, SELECTORS.toastMessage, alertMessages.cart.quantityUpdated);
  }

  async remove_product(productName) {
    const deleteCall = PlaywrightMethods.capture_api_call(this.page, "DELETE", "/carts/*/product/*");
    await PlaywrightMethods.click_on_element_when_visible(this.get_cart_row(productName), SELECTORS.cartRowRemoveButton);
    await PlaywrightMethods.wait_api_call_and_assert_success_status(deleteCall);
    await PlaywrightMethods.assert_toast_message(this.page, SELECTORS.toastMessage, alertMessages.cart.productDeleted);
  }

  async assert_product_in_cart(productName, quantity) {
    const row = this.get_cart_row(productName);
    await PlaywrightMethods.assert_element_visible(row, SELECTORS.cartRowProductTitle);
    await PlaywrightMethods.assert_element_has_value(row, SELECTORS.cartRowQuantityInput, quantity);
  }

  async assert_line_price_and_total(productName, unitPrice, quantity) {
    const row = this.get_cart_row(productName);
    const expectedLinePrice = this.format_price(unitPrice * quantity);
    await PlaywrightMethods.assert_element_has_text(row, SELECTORS.cartRowUnitPrice, this.format_price(unitPrice));
    await PlaywrightMethods.assert_element_has_text(row, SELECTORS.cartRowLinePrice, expectedLinePrice);
    await PlaywrightMethods.assert_element_has_text(this.page, SELECTORS.cartTotal, expectedLinePrice);
  }

  async assert_cart_is_empty(removedProductName) {
    await PlaywrightMethods.assert_text_visible(this.page, alertMessages.cart.emptyCart);
    await expect(this.get_cart_row(removedProductName)).toHaveCount(0);
  }
}
