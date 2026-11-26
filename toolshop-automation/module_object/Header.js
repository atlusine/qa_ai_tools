import { SELECTORS } from "../support/selectors";
import { PlaywrightMethods } from "../support/PlaywrightMethods";

export class Header {
  constructor(page) {
    this.page = page;
  }

  async open_sign_in_page() {
    await PlaywrightMethods.click_on_element_when_visible(this.page, SELECTORS.navSignIn);
    await PlaywrightMethods.assert_page_url_includes_text(this.page, "/auth/login");
  }

  async open_cart() {
    const cartCall = PlaywrightMethods.capture_api_call(this.page, "GET", "/carts/*");
    await PlaywrightMethods.click_on_element_when_visible(this.page, SELECTORS.navCart);
    await PlaywrightMethods.wait_api_call_and_assert_success_status(cartCall);
    await PlaywrightMethods.assert_page_url_includes_text(this.page, "/checkout");
  }

  async assert_cart_quantity_badge(quantity) {
    await PlaywrightMethods.assert_element_has_text(this.page, SELECTORS.cartQuantityBadge, String(quantity));
  }

  async assert_signed_in_user_name(fullName) {
    await PlaywrightMethods.assert_element_contains_text(this.page, SELECTORS.navMenu, fullName);
  }
}
