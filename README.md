country-flag-icons
==================

CSS for svg based country flag icons. See the
[demo](http://lipis.github.io/country-flag-icons/).

CSS classes
-----------


`.flag-icon` sets the correct proportions for the flag icon when used inline
with text.

`.flag-icon-xx` sets the `background-image` with the correct flag, where `xx` is the
[ISO 3166-1-alpha-2 code](http://www.iso.org/iso/country_names_and_code_elements).

`.flag-icon-squared` for the squared version of the flag.

`.flag-icon-background` sets the the background to `position: 50%`,
`repeat:no-repeat` and `size:contain`.


Usage
-----

For using the flags inline with text add the classes `.flag-icon` and `.flag-icon-xx`
to an empty `<span>`. If you want the flag to have the squared version then also add 
the clas `flag-icon-squared`. Example:

    <span class="flag-icon flag-icon-gr"></span>
    <span class="flag-icon flag-icon-gr flag-icon-squared"></span>

You could also apply this to any element, but in that case you'll have to use the 
`flag-icon-background` instead of `flag-icon` and you're set. This will add the 
correct background with the following CSS properties:

    background-size: contain;
    background-position: 50%;
    background-repeat: no-repeat;

Which means that the flag is just going to appear in the middle of an element, so 
you will have to set manually the correct size of 3x4 ratio or if it's squared add also the `flag-icon-squared` class.


Development
-----------

Run the `npm install` to install the dependencies after cloning the project and
you'll be able to:

To watch for changes and live reloed if served

    $ grunt

To build `*.less` files

    $ grunt build

To serve it on `localhost:8000`

    $ grunt connect

To have only specific countries in the css file, remove the ones that you don't 
need from the
[`country-flag-icons-list.less`](https://github.com/lipis/country-flag-icons/blob/master/less/country-flag-icons-list.less)
file and build it again.

Credits
-------

This project wouldn't exist without the awesome collection of svg flags:
[koppi/iso-country-flags-svg-collection](https://github.com/koppi/iso-country-flags-svg-collection)
