// MedLuxLife: Google (Anna, 2026-10-21 – "Google does not show our logo and says nothing about the site")
// Home page (every language): who we are, as structured data – the site name Google shows next to the result, the logo and
// the contact details (only what the Impressum already says). Visitors see nothing of it.
add_action( 'wp_head', function () {
	if ( ! is_front_page() ) {
		return;
	}
	$home = 'https://medluxlife.de/';
	$data = array(
		'@context' => 'https://schema.org',
		'@graph'   => array(
			array(
				'@type'         => 'WebSite',
				'@id'           => $home . '#website',
				'name'          => 'MedLuxLife',
				'alternateName' => array( 'Med Lux Life', 'medluxlife.de' ),
				'url'           => $home,
				'inLanguage'    => array( 'en', 'de', 'tr', 'uk', 'ru', 'ar' ),
				'publisher'     => array( '@id' => $home . '#organization' ),
			),
			array(
				'@type'        => 'Organization',
				'@id'          => $home . '#organization',
				'name'         => 'MedLuxLife',
				'url'          => $home,
				'logo'         => array(
					'@type'  => 'ImageObject',
					'url'    => $home . 'wp-content/uploads/2026/10/medluxlife-favicon-white.png',
					'width'  => 512,
					'height' => 512,
				),
				'image'        => $home . 'wp-content/uploads/2026/10/medluxlife-share-light.jpg',
				'description'  => 'Medical treatments and travel planned for you in one place – specialists, hotels, flights and airport transfers, with a personal coordinator who speaks your language.',
				'email'        => 'info@medluxlife.de',
				'telephone'    => '+49 160 93448714',
				'address'      => array(
					'@type'           => 'PostalAddress',
					'streetAddress'   => 'Stolberger Straße 21',
					'postalCode'      => '52068',
					'addressLocality' => 'Aachen',
					'addressCountry'  => 'DE',
				),
				'contactPoint' => array(
					'@type'             => 'ContactPoint',
					'contactType'       => 'customer service',
					'telephone'         => '+49 160 93448714',
					'email'             => 'info@medluxlife.de',
					'availableLanguage' => array( 'English', 'German', 'Turkish', 'Ukrainian', 'Russian' ),
				),
				'sameAs'       => array( 'https://www.instagram.com/medluxlife/', 'https://www.facebook.com/profile.php?id=61594715669578' ),
			),
		),
	);
	echo '<script type="application/ld+json">' . wp_json_encode( $data, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE ) . "</script>\n";
}, 5 );

// Sitemap: WordPress' own sitemap lists the English pages only. This adds every page in DE, TR, UK, RU and AR
// (same address with the language in front, /de/health/ …) as wp-sitemap-languages-<lang>-1.xml.
// The German legal pages are only listed once (English list), they have no translated version.
add_action( 'init', function () {
	if ( ! function_exists( 'wp_register_sitemap_provider' ) || ! class_exists( 'WP_Sitemaps_Provider' ) ) {
		return;
	}
	if ( ! class_exists( 'Medlux_Language_Sitemap' ) ) {
		class Medlux_Language_Sitemap extends WP_Sitemaps_Provider {
			const LANGS = array( 'de', 'tr', 'uk', 'ru', 'ar' );
			const LEGAL = array( 3, 596, 602, 604, 612, 616 );

			public function __construct() {
				$this->name        = 'languages';
				$this->object_type = 'languages';
			}

			public function get_object_subtypes() {
				$out = array();
				foreach ( self::LANGS as $lang ) {
					$out[ $lang ] = (object) array( 'name' => $lang );
				}
				return $out;
			}

			public function get_url_list( $page_num, $lang = '' ) {
				if ( ! in_array( $lang, self::LANGS, true ) || 1 !== (int) $page_num ) {
					return array();
				}
				$ids = get_posts( array(
					'post_type'    => 'page',
					'post_status'  => 'publish',
					'numberposts'  => -1,
					'fields'       => 'ids',
					'orderby'      => 'ID',
					'order'        => 'ASC',
					'post__not_in' => self::LEGAL,
					'has_password' => false,
				) );
				$out = array();
				foreach ( $ids as $id ) {
					$path  = wp_make_link_relative( get_permalink( $id ) );
					$out[] = array(
						'loc'     => home_url( '/' . $lang . $path ),
						'lastmod' => get_post_modified_time( 'Y-m-d\TH:i:s+00:00', true, $id ),
					);
				}
				return $out;
			}

			public function get_max_num_pages( $lang = '' ) {
				return 1;
			}
		}
	}
	wp_register_sitemap_provider( 'languages', new Medlux_Language_Sitemap() );
} );
