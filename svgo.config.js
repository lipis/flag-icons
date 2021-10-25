module.exports = {
    plugins: [
      {
        name: 'preset-default',
        params: {
          overrides: {
            cleanupIDs: false,
          },
        },
      },
      'sortAttrs',
      'removeDimensions',
      'removeStyleElement',
      'removeScriptElement',
    ],
  };
