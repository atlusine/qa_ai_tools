import { test } from "@playwright/test";
import { users, get_user_password } from "../../support/users";
import { LoginPage } from "../../module_object/LoginPage";
import { Header } from "../../module_object/Header";

test.describe("Customer login", { tag: "@smoke" }, () => {
  test("TC01 Log in as a customer and verify the My account page opens", async ({ page }) => {
    const loginPage = new LoginPage(page);
    const header = new Header(page);
    const customer = users.customer_login;

    await loginPage.open_login_page();
    await loginPage.login(customer.email, get_user_password());
    await loginPage.assert_my_account_page_opened();
    await header.assert_signed_in_user_name(customer.fullName);
  });
});
