export const users = {
  customer_login: {
    email: "customer@practicesoftwaretesting.com",
    fullName: "Jane Doe",
  },
  unregistered_user: {
    email: "not-registered-user@practicesoftwaretesting.com",
  },
};

export function get_user_password() {
  const password = process.env.USER_PASSWORD;
  if (!password) {
    throw new Error("USER_PASSWORD is not set. Copy .env.example to .env");
  }
  return password;
}
