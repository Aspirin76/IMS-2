import js from '@eslint/js'
import reactHooks from 'eslint-plugin-react-hooks'

// 重點：rules-of-hooks 會自動抓出「在元件外呼叫 Hook」這類錯誤
// （本專案曾因此三次白畫面）。
export default [
  { ignores: ['dist', 'node_modules'] },
  js.configs.recommended,
  {
    files: ['src/**/*.{js,jsx}'],
    plugins: { 'react-hooks': reactHooks },
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
      parserOptions: { ecmaFeatures: { jsx: true } },
      globals: {
        window: 'readonly',
        document: 'readonly',
        console: 'readonly',
        fetch: 'readonly',
        setTimeout: 'readonly',
        URLSearchParams: 'readonly',
      },
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      // 本專案刻意用 useEffect + setState 做資料載入（沒有引入資料查詢函式庫），
      // 這條 React Compiler 規則在此不適用；rules-of-hooks 才是要守的。
      'react-hooks/set-state-in-effect': 'off',
      'no-undef': 'off',
      'no-unused-vars': ['warn', { varsIgnorePattern: '^[A-Z_]' }],
    },
  },
]
