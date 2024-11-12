const eslintPluginReact = require('eslint-plugin-react');
const eslintConfigPrettier = require('eslint-config-prettier');

module.exports = [
  {
    ignores: ['node_modules/**']
  },
  {
    files: ['**/*.js', '**/*.jsx'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      parser: require('@babel/eslint-parser'),
      parserOptions: {
        requireConfigFile: false, // Allows parsing without a Babel config
        babelOptions: {
          presets: ['@babel/preset-react'], // Ensures JSX is parsed correctly
        }
      }
    },
    plugins: {
      react: eslintPluginReact
    },
    rules: {
      ...eslintConfigPrettier.rules,
      'react/react-in-jsx-scope': 'off',
      'react/prop-types': 'off'
    }
  }
];
