module.exports = {
  extends: [
    'prettier'
  ],
  plugins: [
    'prettier'
  ],
  settings: {
    es6: true
  },
  env: {
    browser: true,
    node: true,
    es6: true
  },
  globals: {},
  parser: '@babel/eslint-parser',
  parserOptions: {
    allowImportExportEverywhere: false,
    ecmaVersion: 6
  },
  rules: {
    'curly': 'error',
    'prettier/prettier': 'error',
    'no-console': 'warn',
    'no-alert': 'warn',
    'no-unused-vars': [
      'warn',
      {
        varsIgnorePattern: '^_',
        argsIgnorePattern: '^_'
      }
    ],
    'prefer-const': [
      'error',
      {
        destructuring: 'any'
      }
    ],
    'no-debugger': 'warn',
    'one-var': [
      'error',
      {
        initialized: 'never'
      }
    ],
    'no-mixed-operators': 0,
    'require-await': 'error',
    'no-restricted-globals': [
      'error',
      'addEventListener',
      'blur',
      'close',
      'closed',
      'defaultStatus',
      'defaultstatus',
      'event',
      'external',
      'find',
      'focus',
      'frameElement',
      'frames',
      'history',
      'innerHeight',
      'innerWidth',
      'length',
      'location',
      'locationbar',
      'menubar',
      'moveBy',
      'moveTo',
      'name',
      'onblur',
      'onerror',
      'onfocus',
      'onload',
      'onresize',
      'onunload',
      'open',
      'opener',
      'opera',
      'outerHeight',
      'outerWidth',
      'pageXOffset',
      'pageYOffset',
      'parent',
      'print',
      'removeEventListener',
      'resizeBy',
      'resizeTo',
      'screen',
      'screenLeft',
      'screenTop',
      'screenX',
      'screenY',
      'scroll',
      'scrollbars',
      'scrollBy',
      'scrollTo',
      'scrollX',
      'scrollY',
      'self',
      'status',
      'statusbar',
      'stop',
      'toolbar',
      'top'
    ],
    'linebreak-style': ['warn', 'unix']
  }
}
