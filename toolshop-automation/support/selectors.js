const by_test_id = (testId) => ({ kind: "testId", value: testId });
const by_role = (role, name) => ({ kind: "role", role, name });
const by_css_without_test_id = (value) => ({ kind: "css", value });

export const SELECTORS = {
  navSignIn: by_test_id("nav-sign-in"),
  navMenu: by_test_id("nav-menu"),
  navCart: by_test_id("nav-cart"),
  cartQuantityBadge: by_test_id("cart-quantity"),

  searchQueryInput: by_test_id("search-query"),
  searchSubmitButton: by_test_id("search-submit"),
  searchCaption: by_test_id("search-caption"),
  searchNoResults: by_test_id("no-results"),
  sortSelect: by_test_id("sort"),
  categoryCheckbox: by_role("checkbox", "%CATEGORY%"),

  productCardName: by_test_id("product-name"),
  productCardPrice: by_test_id("product-price"),

  productDetailsName: by_test_id("product-name"),
  productDetailsUnitPrice: by_test_id("unit-price"),
  productDetailsQuantityInput: by_test_id("quantity"),
  productDetailsIncreaseQuantityButton: by_test_id("increase-quantity"),
  productDetailsAddToCartButton: by_test_id("add-to-cart"),

  cartRow: by_role("row"),
  cartRowProductTitle: by_test_id("product-title"),
  cartRowQuantityInput: by_test_id("product-quantity"),
  cartRowUnitPrice: by_test_id("product-price"),
  cartRowLinePrice: by_test_id("line-price"),
  cartRowRemoveButton: by_css_without_test_id("a.btn-danger"),
  cartTotal: by_test_id("cart-total"),

  loginEmailInput: by_test_id("email"),
  loginPasswordInput: by_test_id("password"),
  loginSubmitButton: by_test_id("login-submit"),
  loginError: by_test_id("login-error"),

  pageTitle: by_test_id("page-title"),

  registerSubmitButton: by_test_id("register-submit"),
  registerFieldError: by_test_id("%FIELD%-error"),

  toastMessage: by_role("alert"),
};
