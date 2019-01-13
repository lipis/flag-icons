<?php
/*
Plugin Name: Flag Icon CSS
Version: 0.0.5
Author: Bas Bloemsaat
Description: Adds flag-icon-css to wordpress
*/

defined( 'ABSPATH' ) or die( 'No direct access' );


if ( ! class_exists( 'Flag_Icon_CSS' ) ) :
    class Flag_Icon_CSS {
        public function __construct() {
            wp_enqueue_style( 'flag-icon-css', plugins_url( 'css/flag-icon.min.css', __FILE__ ) );

        }
    }

    $flag_icon_css = new Flag_Icon_CSS;

endif;
    