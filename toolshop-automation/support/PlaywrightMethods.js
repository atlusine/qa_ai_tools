import { expect } from "@playwright/test";
import { environment } from "./environment";

const API_CALL_TIMEOUT = 30000;

function substitute_placeholders(value, params) {
  if (typeof value !== "string") return value;
  return value.replace(/%([A-Z_]+)%/g, (match, key) => {
    if (!(key in params)) throw new Error(`Selector placeholder ${match} has no value in ${JSON.stringify(params)}`);
    return String(params[key]);
  });
}

function convert_endpoint_glob_to_regex(endpoint) {
  const escaped = (environment.apiUrl + endpoint).replace(/[.+?^${}()|[\]\\]/g, "\\$&");
  return new RegExp(`^${escaped.replace(/\*\*/g, ".*").replace(/(?<!\.)\*/g, "[^/]*")}(\\?.*)?$`);
}

function parse_price(text) {
  return Number(String(text).replace(/[^0-9.]/g, ""));
}

export class PlaywrightMethods {
  static get_element(scope, selector, params = {}) {
    switch (selector.kind) {
      case "testId":
        return scope.getByTestId(substitute_placeholders(selector.value, params));
      case "role":
        return selector.name === undefined
          ? scope.getByRole(selector.role)
          : scope.getByRole(selector.role, { name: substitute_placeholders(selector.name, params), exact: true });
      case "css":
        return scope.locator(substitute_placeholders(selector.value, params));
      default:
        throw new Error(`Unknown selector kind: ${selector.kind}`);
    }
  }

  static async open_url(page, path = "/") {
    await page.goto(environment.url + path, { waitUntil: "domcontentloaded" });
  }

  static capture_api_call(page, method, endpoint) {
    const pattern = convert_endpoint_glob_to_regex(endpoint);
    return page.waitForResponse((response) => response.request().method() === method && pattern.test(response.url()), {
      timeout: API_CALL_TIMEOUT,
    });
  }

  static async wait_api_call_and_assert_success_status(apiCall) {
    const response = await apiCall;
    expect(response.status(), `${response.request().method()} ${response.url()}`).toBeLessThan(400);
    return response;
  }

  static async click_on_element_when_visible(scope, selector, params) {
    const element = this.get_element(scope, selector, params);
    await expect(element).toBeVisible();
    await element.click();
  }

  static async type_text_into_element_when_visible(scope, selector, text, params) {
    const element = this.get_element(scope, selector, params);
    await expect(element).toBeVisible();
    await element.fill(String(text));
  }

  static async select_option_by_value(scope, selector, value, params) {
    const element = this.get_element(scope, selector, params);
    await expect(element).toBeVisible();
    await element.selectOption(value);
  }

  static async check_checkbox(scope, selector, params) {
    const element = this.get_element(scope, selector, params);
    await element.check();
    await expect(element).toBeChecked();
  }

  static async get_element_text(scope, selector, params) {
    const element = this.get_element(scope, selector, params);
    await expect(element).toBeVisible();
    return (await element.innerText()).trim();
  }

  static async get_all_element_texts(scope, selector, params) {
    const elements = this.get_element(scope, selector, params);
    await expect(elements.first()).toBeVisible();
    return (await elements.allInnerTexts()).map((text) => text.trim());
  }

  static async get_element_price(scope, selector, params) {
    return parse_price(await this.get_element_text(scope, selector, params));
  }

  static async get_all_element_prices(scope, selector, params) {
    return (await this.get_all_element_texts(scope, selector, params)).map(parse_price);
  }

  static async assert_element_visible(scope, selector, params) {
    await expect(this.get_element(scope, selector, params)).toBeVisible();
  }

  static async assert_first_element_visible(scope, selector, params) {
    await expect(this.get_element(scope, selector, params).first()).toBeVisible();
  }

  static async assert_element_has_text(scope, selector, text, params) {
    await expect(this.get_element(scope, selector, params)).toHaveText(text);
  }

  static async assert_element_contains_text(scope, selector, text, params) {
    await expect(this.get_element(scope, selector, params)).toContainText(text);
  }

  static async assert_element_has_value(scope, selector, value, params) {
    await expect(this.get_element(scope, selector, params)).toHaveValue(String(value));
  }

  static async assert_text_visible(scope, text) {
    await expect(scope.getByText(text, { exact: true })).toBeVisible();
  }

  static async assert_toast_message(page, selector, text) {
    await expect(this.get_element(page, selector).filter({ hasText: text }).first()).toBeVisible();
  }

  static async assert_page_url_includes_text(page, text) {
    await expect(page).toHaveURL(new RegExp(text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  }

  static assert_numbers_sorted_ascending(numbers, description) {
    const sorted = [...numbers].sort((a, b) => a - b);
    expect(numbers, description).toEqual(sorted);
  }

  static assert_amount_equals(actual, expected, description) {
    expect(actual, description).toBeCloseTo(expected, 2);
  }
}
