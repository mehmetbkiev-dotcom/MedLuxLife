// MedLuxLife: link previews (WhatsApp, Viber, Telegram, Facebook …) – page title, a short text about us and the branded navy image (media 2069)
add_action( 'wp_head', function () {
	if ( is_admin() || is_feed() ) {
		return;
	}
	$site  = get_bloginfo( 'name' );
	$intro = 'Medical treatments and travel planned for you in one place – specialists, hotels, flights and airport transfers, with a personal coordinator who speaks your language.';
	$title = wp_get_document_title();
	$desc  = $intro;
	$url   = home_url( '/' );
	if ( is_front_page() ) {
		$title = $site . ' – ' . get_bloginfo( 'description' );
	} elseif ( is_singular() ) {
		$post  = get_queried_object();
		$title = get_the_title( $post ) . ' – ' . $site;
		// the page's own excerpt, otherwise its first real paragraph (at least 80 characters, so phone numbers or short labels are skipped)
		$text = has_excerpt( $post ) ? get_the_excerpt( $post ) : '';
		if ( '' === $text && preg_match_all( '#<p[^>]*>(.*?)</p>#s', strip_shortcodes( $post->post_content ), $m ) ) {
			foreach ( $m[1] as $para ) {
				$para = trim( preg_replace( '/\s+/', ' ', html_entity_decode( wp_strip_all_tags( $para ), ENT_QUOTES, 'UTF-8' ) ) );
				if ( strlen( $para ) >= 80 ) {
					$text = $para;
					break;
				}
			}
		}
		if ( '' !== $text ) {
			$desc = wp_trim_words( $text, 30, '…' );
		}
		$url = get_permalink( $post );
	}
	$img = wp_get_attachment_image_src( 2069, 'full' );
	echo "\n<!-- MedLuxLife link preview -->\n";
	printf( '<meta name="description" content="%s" />' . "\n", esc_attr( $desc ) );
	printf( '<meta property="og:type" content="website" />' . "\n" );
	printf( '<meta property="og:site_name" content="%s" />' . "\n", esc_attr( $site ) );
	printf( '<meta property="og:title" content="%s" />' . "\n", esc_attr( $title ) );
	printf( '<meta property="og:description" content="%s" />' . "\n", esc_attr( $desc ) );
	printf( '<meta property="og:url" content="%s" />' . "\n", esc_url( $url ) );
	if ( $img ) {
		printf( '<meta property="og:image" content="%s" />' . "\n", esc_url( $img[0] ) );
		printf( '<meta property="og:image:width" content="%d" />' . "\n", $img[1] );
		printf( '<meta property="og:image:height" content="%d" />' . "\n", $img[2] );
		printf( '<meta property="og:image:alt" content="%s" />' . "\n", esc_attr( get_post_meta( 2069, '_wp_attachment_image_alt', true ) ) );
		printf( '<meta name="twitter:card" content="summary_large_image" />' . "\n" );
		printf( '<meta name="twitter:image" content="%s" />' . "\n", esc_url( $img[0] ) );
	}
	printf( '<meta name="twitter:title" content="%s" />' . "\n", esc_attr( $title ) );
	printf( '<meta name="twitter:description" content="%s" />' . "\n", esc_attr( $desc ) );
}, 5 );
