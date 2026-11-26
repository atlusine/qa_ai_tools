function strip_trailing_slash(url) {
  return url.replace(/\/+$/, "");
}

export const environment = {
  url: strip_trailing_slash(process.env.BASE_URL || "https://practicesoftwaretesting.com"),
  apiUrl: strip_trailing_slash(process.env.API_URL || "https://api.practicesoftwaretesting.com"),
};
