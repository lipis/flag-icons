<?php
/*
Plugin Name: Flag Icon CSS
Version: 0.0.1
Author: Bas Bloemsaat
Description: Adds flag-icon-css to wordpress
*/

defined( 'ABSPATH' ) or die( 'No direct access' );


if ( ! class_exists( 'Flag_Icon_CSS' ) ) :
    class Flag_Icon_CSS {
        public function __construct() {
            add_action( 'wp_enqueue_scripts', array( $this, 'register_styles' ) );
        }

        public static function register_styles( $atts ) {
            wp_register_style( 'flag-icon-css', plugins_url( 'css/flag-icon.min.css', __FILE__ ) );
        }

    }


    