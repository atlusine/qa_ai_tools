import { CatalogPage } from "../module_object/CatalogPage";
import { ProductPage } from "../module_object/ProductPage";
import { Header } from "../module_object/Header";

export class FlowShopping {
  constructor(page) {
    this.page = page;
    this.catalogPage = new CatalogPage(page);
    this.productPage = new ProductPage(page);
    this.header = new Header(page);
  }

  async add_first_catalog_product_to_cart(quantity = 1) {
    await this.catalogPage.open_catalog();
    const product = await this.catalogPage.get_first_product_card_details();
    await this.catalogPage.open_first_product();
    await this.productPage.increase_quantity_to(quantity);
    await this.productPage.add_product_to_cart();
    await this.header.assert_cart_quantity_badge(quantity);
    return product;
  }
}
