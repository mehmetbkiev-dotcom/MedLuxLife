// MedLuxLife: image alt texts on /de/ and /tr/ (the free TranslatePress does not translate them). The translations are a list per language
// in the option medlux_alt_i18n_<lang> (English alt => translation), written by tools/alt_i18n.py; images whose alt is not in the list keep it.
add_filter( 'render_block', function ( $html, $block ) {
	static $map = null;
	if ( false === strpos( $html, '<img' ) || ! class_exists( 'WP_HTML_Tag_Processor' ) ) {
		return $html;
	}
	if ( null === $map ) {
		global $TRP_LANGUAGE;
		$s       = get_option( 'trp_settings' );
		$default = isset( $s['default-language'] ) ? $s['default-language'] : 'en_GB';
		$map     = ( ! empty( $TRP_LANGUAGE ) && $TRP_LANGUAGE !== $default ) ? (array) get_option( 'medlux_alt_i18n_' . strtolower( $TRP_LANGUAGE ), array() ) : array();
	}
	if ( ! $map ) {
		return $html;
	}
	$p       = new WP_HTML_Tag_Processor( $html );
	$changed = false;
	while ( $p->next_tag( 'img' ) ) {
		$alt = $p->get_attribute( 'alt' );
		if ( is_string( $alt ) && isset( $map[ trim( $alt ) ] ) ) {
			$p->set_attribute( 'alt', $map[ trim( $alt ) ] );
			$changed = true;
		}
	}
	return $changed ? $p->get_updated_html() : $html;
}, 20, 2 );
