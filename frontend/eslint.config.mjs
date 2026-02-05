import { defineConfig, flatConfigsToRulesDeps } from "eslint/config";
import next from "eslint-config-next";

const eslintConfig = defineConfig([
  ...next,
  // Override default ignores of eslint-config-next.
  {
    ignores: [
      // Default ignores of eslint-config-next:
      ".next/**",
      "out/**",
      "build/**",
      "next-env.d.ts",
    ],
  },
]);

export default eslintConfig;
