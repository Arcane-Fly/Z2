import js from '@eslint/js';
import tseslint from '@typescript-eslint/eslint-plugin';
import tsparser from '@typescript-eslint/parser';
import react from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import jsxA11y from 'eslint-plugin-jsx-a11y';
import regexp from 'eslint-plugin-regexp';

export default [
  {
    ignores: ['dist/', 'node_modules/', '*.config.js', '*.config.ts', 'e2e/', 'playwright-report/']
  },
  {
    files: ['**/*.{js,jsx,ts,tsx}'],
    languageOptions: {
      parser: tsparser,
      parserOptions: {
        ecmaFeatures: {
          jsx: true
        },
        ecmaVersion: 'latest',
        sourceType: 'module'
      },
      globals: {
        browser: true,
        es2020: true,
        node: true,
        window: true,
        document: true,
        navigator: true,
        console: true,
        setTimeout: true,
        clearTimeout: true,
        setInterval: true,
        clearInterval: true,
        fetch: true,
        Request: true,
        Response: true,
        Headers: true,
        URLSearchParams: true,
        URL: true,
        FormData: true,
        Blob: true,
        File: true,
        FileReader: true,
        localStorage: true,
        sessionStorage: true,
        location: true,
        history: true,
        Element: true,
        HTMLElement: true,
        Node: true,
        Event: true,
        CustomEvent: true,
        KeyboardEvent: true,
        MouseEvent: true,
        Promise: true,
        Symbol: true,
        Map: true,
        Set: true,
        WeakMap: true,
        WeakSet: true,
        Proxy: true,
        Reflect: true,
        Intl: true,
        JSON: true,
        Math: true,
        Date: true,
        RegExp: true,
        Array: true,
        Object: true,
        String: true,
        Number: true,
        Boolean: true,
        Error: true,
        TypeError: true,
        RangeError: true,
        SyntaxError: true,
        ReferenceError: true
      }
    },
    plugins: {
      '@typescript-eslint': tseslint,
      'react': react,
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
      'jsx-a11y': jsxA11y,
      'regexp': regexp
    },
    settings: {
      react: {
        version: 'detect'
      }
    },
    rules: {
      // Base ESLint rules
      'prefer-const': 'error',
      'no-var': 'error',
      'no-console': 'warn',
      
      // React rules
      'react/react-in-jsx-scope': 'off',
      'react/prop-types': 'off',
      'react-hooks/rules-of-hooks': 'error',
      'react-hooks/exhaustive-deps': 'warn',
      'react-refresh/only-export-components': 'warn',
      
      // TypeScript rules
      '@typescript-eslint/no-unused-vars': [
        'error',
        {
          argsIgnorePattern: '^_',
          varsIgnorePattern: '^_'
        }
      ],
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/explicit-function-return-type': 'off',
      '@typescript-eslint/explicit-module-boundary-types': 'off',
      '@typescript-eslint/no-non-null-assertion': 'warn',
      
      // Accessibility rules
      'jsx-a11y/anchor-is-valid': 'warn',
      'jsx-a11y/alt-text': 'error',
      'jsx-a11y/aria-props': 'error',
      'jsx-a11y/aria-proptypes': 'error',
      'jsx-a11y/aria-unsupported-elements': 'error',
      'jsx-a11y/role-has-required-aria-props': 'error',
      'jsx-a11y/role-supports-aria-props': 'error',

      // =======================================================================
      // NO-REGEX-BY-DEFAULT POLICY
      // =======================================================================
      
      // Hard bans on dangerous patterns
      'no-new-wrappers': 'error',
      'no-eval': 'error',
      
      // eslint-plugin-regexp rules (comprehensive regex safety)
      'regexp/no-super-linear-backtracking': 'error',
      'regexp/no-useless-quantifier': 'error',
      'regexp/no-empty-alternative': 'error',
      'regexp/no-dupe-characters-character-class': 'error',
      'regexp/optimal-quantifier-concatenation': 'error',
      'regexp/no-legacy-features': 'error',
      'regexp/no-obscure-range': 'error',
      'regexp/no-misleading-capturing-group': 'warn',
      'regexp/no-useless-assertions': 'warn',
      'regexp/prefer-character-class': 'warn',
      'regexp/prefer-d': 'warn',
      'regexp/prefer-w': 'warn',
      'regexp/prefer-plus-quantifier': 'warn',
      'regexp/prefer-star-quantifier': 'warn',
      'regexp/prefer-question-quantifier': 'warn',
      
      // Discourage any regex usage - must be explicitly whitelisted
      'no-restricted-syntax': [
        'error',
        {
          selector: "NewExpression[callee.name='RegExp']",
          message: 'new RegExp() is disallowed by default. Use a parser (URL, JSON, DOMParser) or approved helper. If truly needed, document exception in CONTRIBUTING.md and use anchored, literal patterns only.'
        },
        {
          selector: "Literal[regex=true][value.raw=/.*\\.\\*.*|.*\\(\\.\\*\\).*/]",
          message: 'Catch-all patterns (.*) are disallowed - they are too broad and prone to catastrophic backtracking. Use specific parsers instead.'
        },
        {
          selector: "Literal[regex=true][value.raw=/.*\\(\\?[<=!].*/]",
          message: 'Lookbehind and lookahead assertions are disallowed - they are complex and error-prone. Use string methods or parsers instead.'
        }
      ],
      
      // Discourage regex-based string methods
      'no-restricted-properties': [
        'error',
        {
          object: 'String',
          property: 'match',
          message: 'String.match() with regex is discouraged. Use typed parsing APIs: new URL() for URLs, JSON.parse() for JSON, DOMParser for HTML, or string methods like includes/startsWith/endsWith.'
        },
        {
          object: 'String',
          property: 'replace',
          message: 'String.replace() with regex is discouraged. Use explicit string methods or transformations. For multiple replacements, use replaceAll() with string literals.'
        },
        {
          object: 'String',
          property: 'search',
          message: 'String.search() with regex is discouraged. Use indexOf(), includes(), startsWith(), or endsWith() for simple string searching.'
        },
        {
          object: 'String',
          property: 'split',
          message: 'String.split() with regex is discouraged. For structured data, use proper parsers (csv-parse, JSON.parse). For simple splits, use string literals.'
        }
      ]
    }
  },
  // Relaxed rules for test files - they may need to test regex behavior
  {
    files: ['**/*.test.{js,jsx,ts,tsx}', '**/*.spec.{js,jsx,ts,tsx}', '**/__tests__/**'],
    rules: {
      'regexp/no-super-linear-backtracking': 'warn', // Allow in tests but warn
      'no-restricted-syntax': 'off', // Allow regex in tests
      'no-restricted-properties': 'off' // Allow regex methods in tests
    }
  }
];
