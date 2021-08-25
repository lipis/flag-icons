# Contributing

Thank you for choosing to contribute to this library. The main purpose of this library is to provide country flags in SVG format, along with CSS for easy integration in web platforms. This library is licensed under the [MIT license](https://github.com/lipis/flag-icon-css/blob/master/LICENSE), and by contributing, you agree that your contributions are subject to the terms of the MIT license.

## Can I add this flag?

Please note this library is intended to host flags for countries that have been officially assigned an [ISO 3166-1 alpha-2 country code](https://www.iso.org/obp/ui/). As of the latest revision to the ISO standard, this library already includes all 249 officially assigned countries.

Transitionally reserved ISO 3166-1 alpha-2 country codes will not be accepted, as these are intended to be used only in a transitional period as they have been superceded. This applies to the following country codes:

- AN: Netherlands Antilles
- BU: Burma
- CS: Czechoslovakia / Serbia and Montenegro
- NT: Neutral Zone
- SF: Finland
- TP: East Timor
- YU: Yugoslavia
- ZR: Zaire

Exceptionally reserved ISO 3166-1 alpha-2 country codes may be added to the library if deemed necessary.

Flags for countries or representation not defined by the ISO 3166-1 standard will not be accepted.

## Contributing Guidelines

### Contributing a New Flag

If you are contributing a new flag that falls within the guidelines stated above, please make sure you are adding the flag to each necessary component of the project or reviewing of your pull request may be delayed:

1. Ensure that you have created a flag for each of the aspect ratios provided by the library (1:1 and 4:3).
2. Please run your SVG files through svgo using the configuration provided in the root of the project. The package provides a runnable task that will use the configuration provided. You can run this task by using the following command: `npm run svgo`.
3. To prevent breaking the display of flags when the SVGs are used inline, clip-path IDs should be unique to each flag. The ID should be prefixed with the countries ISO 3166-1 alpha-2 country code. For example, if you are making a flag for Antigua and Barbuda (country code `AG`), the first clip-path ID might be optimized to `<clipPath id="a">`. You will need to change this to `<clipPath id="ag-a">`, and so forth for each subsequent clip-path ID, if applicable. **This is only applicable to SVG files using clip-paths.**
4. The header should define the XML namespace, the CSS ID, and the viewbox (0 0 512 512 for 1:1 flags, and 0 0 640 480 for 4:3 flags). If you are developing a 1:1 flag for Antigua and Barbuda, the header should look like the following:
`<svg xmlns="http://www.w3.org/2000/svg" id="flag-icon-css-ag" viewBox="0 0 512 512">`
5. You are most likely contributing a flag for an exceptionally reserved ISO 3166-1 alpha-2 country code, so it will need to be added under the "Other flags" section of the following files (Countries officially assigned will be added to the regular section):
- [flag-icon.css](https://github.com/lipis/flag-icon-css/blob/master/css/flag-icon.css) and [flag-icon.min.css](https://github.com/lipis/flag-icon-css/blob/master/css/flag-icon.min.css)
- [flag-icon-more.less](https://github.com/lipis/flag-icon-css/blob/master/less/flag-icon-more.less)
- [_flag-icon-list.scss](https://github.com/lipis/flag-icon-css/blob/master/sass/_flag-icon-list.scss)
- [index.html](https://github.com/lipis/flag-icon-css/blob/master/index.html)

### Updating an Existing Flag

If you are updating an existing flag, it will mostly resemble the steps above, without adding references to the flag anywhere.

1. Ensure that you have edited the flag for each of the aspect ratios provided by the library (1:1 and 4:3).
2. Please run your SVG files through svgo using the configuration provided in the root of the project. The package provides a runnable task that will use the configuration provided. You can run this task by using the following command: `npm run svgo`.
3. To prevent breaking the display of flags when the SVGs are used inline, clip-path IDs should be unique to each flag. The ID should be prefixed with the countries ISO 3166-1 alpha-2 country code. For example, if you are making a flag for Antigua and Barbuda (country code `AG`), the first clip-path ID might be optimized to `<clipPath id="a">`. You will need to change this to `<clipPath id="ag-a">`, and so forth for each subsequent clip-path ID, if applicable. **This is only applicable to SVG files using clip-paths.**
4. The header should define the XML namespace, the CSS ID, and the viewbox (0 0 512 512 for 1:1 flags, and 0 0 640 480 for 4:3 flags). If you are developing a 1:1 flag for Antigua and Barbuda, the header should look like the following:
`<svg xmlns="http://www.w3.org/2000/svg" id="flag-icon-css-ag" viewBox="0 0 512 512">`