import { test } from "@playwright/test";
import { users } from "../../support/users";
import { LoginPage } from "../../module_object/LoginPage";
import { RegisterPage } from "../../module_object/RegisterPage";

test.describe("Authentication validation", { tag: "@regression" }, () => {
  let invalidPassword;

  test.beforeAll("Test data preparation", () => {
    invalidPassword = `invalid-${Date.now()}`;
  });

  test("TC07 Log in with an unknown account and verify the credentials error", async ({ page }) => {
    const loginPage = new LoginPage(page);

    await loginPage.open_login_page();
    await loginPage.login_with_invalid_credentials(users.unregistered_user.email, invalidPassword);
    await loginPage.assert_invalid_credentials_error();
  });

  test("TC08 Submit an empty registration form and verify required field errors", async ({ page }) => {
    const registerPage = new RegisterPage(page);

    await registerPage.open_register_page();
    await registerPage.submit_empty_registration_form();
    await registerPage.assert_required_field_errors();
  });
});
