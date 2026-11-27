import js from "@eslint/js";
import globals from "globals";

export default [
  { ignores: ["node_modules/**", "report/**", "test-results/**", "test-reports/**", "blob-report/**"] },
  js.configs.recommended,
  {
    files: ["**/*.js"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: { ...globals.node },
    },
  },
  {
    files: ["playwright.config.js"],
    languageOptions: { sourceType: "commonjs" },
  },
];
