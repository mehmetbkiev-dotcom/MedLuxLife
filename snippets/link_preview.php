// MedLuxLife: link previews (WhatsApp, Viber, Telegram, Facebook …) – page title, a short text about us and the branded navy image (media 2069)
// On /de/ and /tr/ the title and description come from the reviewed TranslatePress translations (the free plugin does not translate <title> or meta tags).
function medlux_meta_lang() {
	global $TRP_LANGUAGE;
	if ( defined( 'MEDLUX_XLANG' ) && MEDLUX_XLANG ) {
		return 'xl_' . MEDLUX_XLANG;   // /uk/, /ru/ and /ar/ (snippets/xlang.php)
	}
	$s = get_option( 'trp_settings' );
	$default = isset( $s['default-language'] ) ? $s['default-language'] : 'en_GB';
	return ( ! empty( $TRP_LANGUAGE ) && $TRP_LANGUAGE !== $default ) ? $TRP_LANGUAGE : '';
}
function medlux_meta_tr( $s ) {
	global $wpdb;
	static $cache = array();
	$lang = medlux_meta_lang();
	$s    = (string) $s;
	if ( '' === $lang || '' === trim( $s ) ) {
		return $s;
	}
	if ( 0 === strpos( $lang, 'xl_' ) ) {
		$map = function_exists( 'medlux_xlang_map' ) ? medlux_xlang_map() : array();
		$k   = trim( preg_replace( '/\s+/', ' ', $s ) );
		foreach ( array( $k, str_replace( '&#038;', '&amp;', $k ) ) as $key ) {
			if ( isset( $map[ $key ] ) ) {
				return $map[ $key ];
			}
		}
		return null;
	}
	$t = $wpdb->prefix . 'trp_dictionary_en_gb_' . strtolower( $lang );
	if ( ! isset( $cache[ $t ][ $s ] ) ) {
		$v = $wpdb->get_var( $wpdb->prepare( "SELECT translated FROM `$t` WHERE original = %s AND status = 2 AND translated <> '' LIMIT 1", $s ) );
		$cache[ $t ][ $s ] = $v ? $v : null;
	}
	return $cache[ $t ][ $s ];
}
// texts that are not on any page
function medlux_meta_fixed( $key, $en ) {
	$fixed = array(
		'de_DE' => array(
			'intro'   => 'Medizinische Behandlungen und Reisen an einem Ort für Sie geplant – Fachärzte, Hotels, Flüge und Flughafentransfers, mit einer persönlichen Ansprechperson, die Ihre Sprache spricht.',
			'tagline' => 'Gesundheit · Tourismus · Erlebnis',
		),
		'xl_uk' => array(
			'intro'   => 'Медичні процедури та подорожі, сплановані для вас в одному місці – лікарі-фахівці, готелі, перельоти й трансфери з аеропорту, з особистим координатором, який говорить вашою мовою.',
			'tagline' => "Здоров'я · Туризм · Враження",
		),
		'xl_ru' => array(
			'intro'   => 'Медицинские процедуры и путешествия, спланированные для вас в одном месте – врачи-специалисты, отели, перелёты и трансферы из аэропорта, с личным координатором, который говорит на вашем языке.',
			'tagline' => 'Здоровье · Туризм · Впечатления',
		),
		'xl_ar' => array(
			'intro'   => 'علاجات طبية ورحلات سفر نخطط لها من أجلكم في مكان واحد – أطباء مختصون وفنادق ورحلات طيران ونقل من المطار، مع منسّق شخصي يرافقكم في كل خطوة.',
			'tagline' => 'الصحة · السياحة · التجربة',
		),
		'tr_TR' => array(
			'intro'   => 'Tıbbi tedaviler ve seyahat, sizin için tek bir yerde planlanır – uzman hekimler, oteller, uçuşlar ve havalimanı transferleri, sizin dilinizi konuşan kişisel bir koordinatörle.',
			'tagline' => 'Sağlık · Turizm · Deneyim',
		),
	);
	$lang = medlux_meta_lang();
	return isset( $fixed[ $lang ][ $key ] ) ? $fixed[ $lang ][ $key ] : $en;
}
// browser tab title
add_filter( 'document_title_parts', function ( $parts ) {
	if ( '' === medlux_meta_lang() ) {
		return $parts;
	}
	if ( isset( $parts['title'] ) ) {
		$t = medlux_meta_tr( $parts['title'] );
		if ( $t ) {
			$parts['title'] = $t;
		}
	}
	if ( isset( $parts['tagline'] ) ) {
		$parts['tagline'] = medlux_meta_fixed( 'tagline', $parts['tagline'] );
	}
	return $parts;
}, 20 );
add_action( 'wp_head', function () {
	if ( is_admin() || is_feed() ) {
		return;
	}
	$site  = get_bloginfo( 'name' );
	$intro = medlux_meta_fixed( 'intro', 'Medical treatments and travel planned for you in one place – specialists, hotels, flights and airport transfers, with a personal coordinator who speaks your language.' );
	$title = wp_get_document_title();
	$desc  = $intro;
	$url   = home_url( '/' );
	if ( is_front_page() ) {
		$title = $site . ' – ' . medlux_meta_fixed( 'tagline', get_bloginfo( 'description' ) );
	} elseif ( is_singular() ) {
		$post  = get_queried_object();
		$name  = get_the_title( $post );
		$tname = medlux_meta_tr( $name );
		$title = html_entity_decode( $tname ? $tname : $name, ENT_QUOTES, 'UTF-8' ) . ' – ' . $site;
		$lang  = medlux_meta_lang();
		// the page's own excerpt, otherwise its first real paragraph (at least 80 characters, so phone numbers or short labels are skipped)
		$text = has_excerpt( $post ) ? get_the_excerpt( $post ) : '';
		if ( '' !== $text && '' !== $lang ) {
			$tx   = medlux_meta_tr( $text );
			$text = $tx ? $tx : '';
		}
		if ( '' === $text && preg_match_all( '#<p[^>]*>(.*?)</p>#s', strip_shortcodes( $post->post_content ), $m ) ) {
			foreach ( $m[1] as $para ) {
				if ( '' !== $lang ) {
					// the translated paragraph; untranslated ones are skipped
					$tp = medlux_meta_tr( wptexturize( trim( $para ) ) );
					if ( ! $tp ) {
						continue;
					}
					$para = $tp;
				}
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
		// Health and Travel: the one-sentence intros from the home page (Anna, 2026-10-17)
		$fixed = array(
			27 => 'We organize every detail of your treatment so you can focus entirely on your recovery.',
			25 => 'All your travel logistics sorted, so you can simply relax and enjoy.',
		);
		if ( isset( $fixed[ $post->ID ] ) ) {
			$fx   = medlux_meta_tr( $fixed[ $post->ID ] );
			$desc = ( '' === $lang ) ? $fixed[ $post->ID ] : ( $fx ? $fx : $intro );
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
