// MedLuxLife: speed (Anna, 2026-10-20 – IONOS website check "Be quick" 14/100)
// Home hero photo (media 2042): on phones and tablets (≤781px) it is hidden and the portrait crop is shown as CSS background instead
// (global styles), so the browser only needs a tiny version of the hidden image there.
add_filter( 'wp_calculate_image_sizes', function ( $sizes, $size, $src, $meta, $attachment_id ) {
	if ( 2042 === (int) $attachment_id ) {
		return '(max-width: 781px) 2px, 100vw';
	}
	return $sizes;
}, 10, 5 );

// WordPress emoji script (22 KB on every page): not needed, current browsers show emoji themselves
remove_action( 'wp_head', 'print_emoji_detection_script', 7 );
remove_action( 'wp_print_styles', 'print_emoji_styles' );
