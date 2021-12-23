# flag-icons

> A curated collection of all country flags in SVG — plus the CSS for easier integration. See the [demo](https://flagicons.lipis.dev).

## Install

You can either [download](https://github.com/lipis/flag-icons/archive/main.zip) the whole project as is or install it via npm or Yarn:

```bash
npm install --dev flag-icons
# or
yarn add --dev flag-icons
```

## Usage

For using the flags inline with text add the classes `.fi` and `.fi-xx` (where `xx` is the [ISO 3166-1-alpha-2 code](https://www.iso.org/obp/ui/#search/code/) of a country) to an empty `<span>`. If you want to have a squared version flag then add the class `fis` as well. Example:

```html
<span class="fi fi-gr"></span> <span class="fi fi-gr fis"></span>
```

You could also apply this to any element, but in that case you'll have to use the `fib` instead of `fi` and you're set. This will add the correct background with the following CSS properties:

```css
background-size: contain;
background-position: 50%;
background-repeat: no-repeat;
```

Which means that the flag is just going to appear in the middle of an element, so you will have to set manually the correct size of 4 by 3 ratio or if it's squared add also the `flag-icon-squared` class.

## Development

Run the `yarn` to install the dependencies after cloning the project and you'll be able to:

To build `*.less` files

```bash
$ yarn build
```

To serve it on `localhost:8000`

```bash
$ yarn start
```

To have only specific countries in the css file, remove the ones that you don't need from the [`flag-icons-list.less`](less/flag-icons-list.less) file and build it again.

## Credits

- This project wouldn't exist without the awesome and now deleted collection of SVG flags by [koppi](https://github.com/koppi).
- Thank you [Andrejs Abrickis](https://twitter.com/andrejsabrickis) for providing the `flag-icons` name on [npm](https://www.npmjs.com/package/flag-icons).
