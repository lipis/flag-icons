flag-icon-css
=============

CSS for vector based country flags. See the
[demo](http://lipis.github.io/flag-icon-css/).

Usage
-----

For using the flags inline with text add the classes `.flag-icon` and
`.flag-icon-xx` (where `xx` is the
[ISO 3166-1-alpha-2 code](http://www.iso.org/iso/country_names_and_code_elements)
of a country) to an empty `<span>`. If you want to have a squared version flag
then add the class `flag-icon-squared` as well. Example:

    <span class="flag-icon flag-icon-gr"></span>
    <span class="flag-icon flag-icon-gr flag-icon-squared"></span>

You could also apply this to any element, but in that case you'll have to use the
`flag-icon-background` instead of `flag-icon` and you're set. This will add the
correct background with the following CSS properties:

    background-size: contain;
    background-position: 50%;
    background-repeat: no-repeat;

Which means that the flag is just going to appear in the middle of an element, so
you will have to set manually the correct size of 4 by 3 ratio or if it's squared
add also the `flag-icon-squared` class.


Development
-----------

Run the `npm install` to install the dependencies after cloning the project and
you'll be able to:

To watch for changes and live reload if served

    $ grunt

To build `*.less` or `*.scss` files

    $ grunt build

To serve it on `localhost:8000`

    $ grunt connect

To have only specific countries in the css file, remove the ones that you don't
need from the
[`flag-icon-list.less`](https://github.com/lipis/flag-icon-css/blob/master/less/flag-icon-list.less) or
[`flag-icon-list.scss`](https://github.com/lipis/flag-icon-css/blob/master/sass/flag-icon-list.scss)
file and build it again.
