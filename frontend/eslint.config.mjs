import { dirname } from "path"
import { fileURLToPath } from "url"
import { FlatCompat } from "@eslint/eslintrc"

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

const compat = new FlatCompat({ baseDirectory: __dirname })

const config = [
  ...compat.extends("next/core-web-vitals", "next/typescript"),
  {
    rules: {
      // Hard limit: no file may exceed 300 lines. Enforced by CI (npm run lint).
      // NEVER disable or increase this limit — split the module instead.
      "max-lines": ["error", { max: 300, skipBlankLines: false, skipComments: false }],
    },
  },
]

export default config
