import { SELECTORS } from "../support/selectors";
import { alertMessages } from "../support/messages";
import { PlaywrightMethods } from "../support/PlaywrightMethods";

export class ProductPage {
  constructor(page) {
    this.page = page;
  }

  async increase_quantity_to(quantity) {
    const input = PlaywrightMethods.get_element(this.page, SELECTORS.productDetailsQuantityInput);
    while (Number(await input.inputValue()) < quantity) {
      await PlaywrightMethods.click_on_element_when_visible(this.page, SELECTORS.productDetailsIncreaseQuantityButton);
    }
    await PlaywrightMethods.assert_element_has_value(this.page, SELECTORS.productDetailsQuantityInput, quantity);
  }

  async add_product_to_cart() {
    const addToCartCall = PlaywrightMethods.capture_api_call(this.page, "POST", "/carts/*");
    await PlaywrightMethods.click_on_element_when_visible(this.page, SELECTORS.productDetailsAddToCartButton);
    await PlaywrightMethods.wait_api_call_and_assert_success_status(addToCartCall);
    await PlaywrightMethods.assert_toast_message(this.page, SELECTORS.toastMessage, alertMessages.cart.productAdded);
  }

  async get_product_unit_price() {
    return PlaywrightMethods.get_element_price(this.page, SELECTORS.productDetailsUnitPrice);
  }

  async assert_product_details(name, price) {
    await PlaywrightMethods.assert_element_has_text(this.page, SELECTORS.productDetailsName, name);
    PlaywrightMethods.assert_amount_equals(await this.get_product_unit_price(), price, "unit price on the product page");
  }
}
