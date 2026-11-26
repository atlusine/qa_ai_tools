import { SELECTORS } from "../support/selectors";
import { alertMessages, pageTitles } from "../support/messages";
import { PlaywrightMethods } from "../support/PlaywrightMethods";

export class LoginPage {
  constructor(page) {
    this.page = page;
  }

  async open_login_page() {
    await PlaywrightMethods.open_url(this.page, "/auth/login");
    await PlaywrightMethods.assert_element_visible(this.page, SELECTORS.loginEmailInput);
  }

  async submit_credentials(email, password) {
    const loginCall = PlaywrightMethods.capture_api_call(this.page, "POST", "/users/login");
    await PlaywrightMethods.type_text_into_element_when_visible(this.page, SELECTORS.loginEmailInput, email);
    await PlaywrightMethods.type_text_into_element_when_visible(this.page, SELECTORS.loginPasswordInput, password);
    await PlaywrightMethods.click_on_element_when_visible(this.page, SELECTORS.loginSubmitButton);
    return loginCall;
  }

  async login(email, password) {
    const loginCall = await this.submit_credentials(email, password);
    await PlaywrightMethods.wait_api_call_and_assert_success_status(loginCall);
  }

  async login_with_invalid_credentials(email, password) {
    const loginCall = await this.submit_credentials(email, password);
    await loginCall;
  }

  async assert_my_account_page_opened() {
    await PlaywrightMethods.assert_page_url_includes_text(this.page, "/account");
    await PlaywrightMethods.assert_element_has_text(this.page, SELECTORS.pageTitle, pageTitles.myAccount);
  }

  async assert_invalid_credentials_error() {
    await PlaywrightMethods.assert_element_has_text(this.page, SELECTORS.loginError, alertMessages.login.invalidCredentials);
    await PlaywrightMethods.assert_page_url_includes_text(this.page, "/auth/login");
  }
}
