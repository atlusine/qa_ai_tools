import { expect } from "@playwright/test";
import { SELECTORS } from "../support/selectors";
import { alertMessages } from "../support/messages";
import { PlaywrightMethods } from "../support/PlaywrightMethods";

export class CatalogPage {
  sortValues = {
    priceLowToHigh: "price,asc",
  };

  constructor(page) {
    this.page = page;
  }

  async open_catalog() {
    const productsCall = PlaywrightMethods.capture_api_call(this.page, "QUERY", "/products");
    await PlaywrightMethods.open_url(this.page, "/");
    await PlaywrightMethods.wait_api_call_and_assert_success_status(productsCall);
    await PlaywrightMethods.assert_first_element_visible(this.page, SELECTORS.productCardName);
  }

  async search_for_product(term) {
    const searchCall = PlaywrightMethods.capture_api_call(this.page, "QUERY", "/products/search");
    await PlaywrightMethods.type_text_into_element_when_visible(this.page, SELECTORS.searchQueryInput, term);
    await PlaywrightMethods.click_on_element_when_visible(this.page, SELECTORS.searchSubmitButton);
    await PlaywrightMethods.wait_api_call_and_assert_success_status(searchCall);
  }

  async sort_products_by_price_low_to_high() {
    const productsCall = PlaywrightMethods.capture_api_call(this.page, "QUERY", "/products");
    await PlaywrightMethods.select_option_by_value(this.page, SELECTORS.sortSelect, this.sortValues.priceLowToHigh);
    await PlaywrightMethods.wait_api_call_and_assert_success_status(productsCall);
  }

  async filter_products_by_category(category) {
    const productsCall = PlaywrightMethods.capture_api_call(this.page, "QUERY", "/products");
    await PlaywrightMethods.check_checkbox(this.page, SELECTORS.categoryCheckbox, { CATEGORY: category });
    await PlaywrightMethods.wait_api_call_and_assert_success_status(productsCall);
  }

  async get_first_product_card_details() {
    const name = (await PlaywrightMethods.get_all_element_texts(this.page, SELECTORS.productCardName))[0];
    const price = (await PlaywrightMethods.get_all_element_prices(this.page, SELECTORS.productCardPrice))[0];
    return { name, price };
  }

  async open_first_product() {
    const firstCard = PlaywrightMethods.get_element(this.page, SELECTORS.productCardName).first();
    await expect(firstCard).toBeVisible();
    await firstCard.click();
    await PlaywrightMethods.assert_page_url_includes_text(this.page, "/product/");
  }

  async assert_search_caption(term) {
    await PlaywrightMethods.assert_element_has_text(this.page, SELECTORS.searchCaption, alertMessages.search.caption(term));
  }

  async assert_every_product_name_contains(text) {
    const expected = text.toLowerCase();
    await expect
      .poll(async () => {
        const names = await PlaywrightMethods.get_all_element_texts(this.page, SELECTORS.productCardName);
        return names.length > 0 && names.every((name) => name.toLowerCase().includes(expected));
      }, { message: `every product name should contain "${text}"` })
      .toBe(true);
  }

  async assert_product_prices_sorted_ascending() {
    await expect
      .poll(async () => {
        const prices = await PlaywrightMethods.get_all_element_prices(this.page, SELECTORS.productCardPrice);
        return prices.every((price, index) => index === 0 || prices[index - 1] <= price);
      }, { message: "product prices should be sorted from low to high" })
      .toBe(true);
  }
}
