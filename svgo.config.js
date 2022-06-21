module.exports = {
  plugins: [
    {
      name: "preset-default",
      params: {
        overrides: {
          cleanupIDs: false,
        },
      },
    },
    "convertStyleToAttrs",
    "removeDimensions",
    "removeScriptElement",
    "removeStyleElement",
    "sortAttrs",
  ],
};
