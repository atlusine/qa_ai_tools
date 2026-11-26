import { SELECTORS } from "../support/selectors";
import { validationMessages } from "../support/messages";
import { PlaywrightMethods } from "../support/PlaywrightMethods";

export class RegisterPage {
  requiredFieldErrors = {
    "first-name": validationMessages.register.firstNameRequired,
    "last-name": validationMessages.register.lastNameRequired,
    email: validationMessages.register.emailRequired,
    password: validationMessages.register.passwordRequired,
  };

  constructor(page) {
    this.page = page;
  }

  async open_register_page() {
    await PlaywrightMethods.open_url(this.page, "/auth/register");
    await PlaywrightMethods.assert_element_visible(this.page, SELECTORS.registerSubmitButton);
  }

  async submit_empty_registration_form() {
    await PlaywrightMethods.click_on_element_when_visible(this.page, SELECTORS.registerSubmitButton);
  }

  async assert_required_field_errors() {
    for (const [field, message] of Object.entries(this.requiredFieldErrors)) {
      await PlaywrightMethods.assert_element_contains_text(this.page, SELECTORS.registerFieldError, message, { FIELD: field });
    }
    await PlaywrightMethods.assert_page_url_includes_text(this.page, "/auth/register");
  }
}
