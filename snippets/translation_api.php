// MedLuxLife: read/write TranslatePress translations over REST, administrators only (used by tools/trp.py for the DE/TR translation, 2026-10-18)
add_action( 'rest_api_init', function () {
	$perm  = function () { return current_user_can( 'manage_options' ); };
	$table = function ( $lang ) {
		global $wpdb;
		return $wpdb->prefix . 'trp_dictionary_en_gb_' . strtolower( preg_replace( '/[^a-zA-Z_]/', '', (string) $lang ) );
	};
	register_rest_route( 'medlux/v1', '/trp/info', array(
		'methods'             => 'GET',
		'permission_callback' => $perm,
		'callback'            => function () {
			global $wpdb;
			$counts = array();
			foreach ( $wpdb->get_col( "SHOW TABLES LIKE '{$wpdb->prefix}trp\\_%'" ) as $t ) {
				$counts[ $t ] = (int) $wpdb->get_var( "SELECT COUNT(*) FROM `$t`" );
			}
			$s = get_option( 'trp_settings' );
			return array(
				'version'   => defined( 'TRP_PLUGIN_VERSION' ) ? TRP_PLUGIN_VERSION : null,
				'default'   => isset( $s['default-language'] ) ? $s['default-language'] : null,
				'languages' => isset( $s['translation-languages'] ) ? $s['translation-languages'] : null,
				'url_slugs' => isset( $s['url-slugs'] ) ? $s['url-slugs'] : null,
				'tables'    => $counts,
				'mt'        => get_option( 'trp_machine_translation_settings' ),
			);
		},
	) );
	register_rest_route( 'medlux/v1', '/trp/strings', array(
		'methods'             => 'GET',
		'permission_callback' => $perm,
		'callback'            => function ( $r ) use ( $table ) {
			global $wpdb;
			$t      = $table( $r['lang'] );
			$offset = max( 0, intval( $r['offset'] ) );
			$limit  = min( 2000, max( 1, intval( $r['limit'] ? $r['limit'] : 500 ) ) );
			$where  = ( null === $r['status'] ) ? '1=1' : $wpdb->prepare( 'status = %d', intval( $r['status'] ) );
			return array(
				'table' => $t,
				'total' => (int) $wpdb->get_var( "SELECT COUNT(*) FROM `$t` WHERE $where" ),
				'rows'  => $wpdb->get_results( "SELECT id, original, translated, status, block_type, original_id FROM `$t` WHERE $where ORDER BY id LIMIT $offset, $limit", ARRAY_A ),
			);
		},
	) );
	register_rest_route( 'medlux/v1', '/trp/meta', array(
		'methods'             => 'GET',
		'permission_callback' => $perm,
		'callback'            => function ( $r ) {
			global $wpdb;
			$m = $wpdb->prefix . 'trp_original_meta';
			$offset = max( 0, intval( $r['offset'] ) );
			$limit  = min( 5000, max( 1, intval( $r['limit'] ? $r['limit'] : 1000 ) ) );
			return array(
				'keys' => $wpdb->get_results( "SELECT meta_key, COUNT(*) n FROM `$m` GROUP BY meta_key", ARRAY_A ),
				'rows' => $wpdb->get_results( "SELECT original_id, meta_key, meta_value FROM `$m` ORDER BY meta_id LIMIT $offset, $limit", ARRAY_A ),
			);
		},
	) );
	register_rest_route( 'medlux/v1', '/trp/translate', array(
		'methods'             => 'POST',
		'permission_callback' => $perm,
		'callback'            => function ( $r ) use ( $table ) {
			global $wpdb;
			$t = $table( $r['lang'] );
			$n = 0;
			foreach ( (array) $r['items'] as $it ) {
				$n += (int) $wpdb->update( $t, array( 'translated' => (string) $it['translated'], 'status' => 2 ), array( 'id' => intval( $it['id'] ) ) );
			}
			return array( 'updated' => $n );
		},
	) );
	register_rest_route( 'medlux/v1', '/trp/find', array(
		'methods'             => 'GET',
		'permission_callback' => $perm,
		'callback'            => function ( $r ) {
			global $wpdb;
			$q   = '%' . $wpdb->esc_like( (string) $r['q'] ) . '%';
			$out = array();
			foreach ( $wpdb->get_col( "SHOW TABLES LIKE '{$wpdb->prefix}trp\\_%'" ) as $t ) {
				$cols = $wpdb->get_col( "SHOW COLUMNS FROM `$t`" );
				$like = array();
				foreach ( array( 'original', 'translated', 'meta_value' ) as $col ) {
					if ( in_array( $col, $cols, true ) ) {
						$like[] = $wpdb->prepare( "`$col` LIKE %s", $q );
					}
				}
				if ( $like ) {
					$rows = $wpdb->get_results( "SELECT * FROM `$t` WHERE " . implode( ' OR ', $like ) . ' LIMIT 20', ARRAY_A );
					if ( $rows ) {
						$out[ $t ] = $rows;
					}
				}
			}
			return $out;
		},
	) );
	// image alt texts for /de/ and /tr/ (option medlux_alt_i18n_<lang>, read by snippets/alt_i18n.php; written by tools/alt_i18n.py)
	register_rest_route( 'medlux/v1', '/alts', array(
		array(
			'methods'             => 'GET',
			'permission_callback' => $perm,
			'callback'            => function ( $r ) {
				return (array) get_option( 'medlux_alt_i18n_' . strtolower( preg_replace( '/[^a-zA-Z_]/', '', (string) $r['lang'] ) ), array() );
			},
		),
		array(
			'methods'             => 'POST',
			'permission_callback' => $perm,
			'callback'            => function ( $r ) {
				$map = array();
				foreach ( (array) $r['map'] as $en => $tr ) {
					$map[ trim( (string) $en ) ] = sanitize_text_field( (string) $tr );
				}
				update_option( 'medlux_alt_i18n_' . strtolower( preg_replace( '/[^a-zA-Z_]/', '', (string) $r['lang'] ) ), $map, false );
				return array( 'saved' => count( $map ) );
			},
		),
	) );
	// Ukrainian / Russian / Arabic lists for snippets/xlang.php (option medlux_xlang_<lang>, {English text: translation}); written by tools/xlang.py
	register_rest_route( 'medlux/v1', '/xlang', array(
		array(
			'methods'             => 'GET',
			'permission_callback' => $perm,
			'callback'            => function ( $r ) {
				$m = (array) get_option( 'medlux_xlang_' . ( in_array( $r['lang'], array( 'ru', 'ar' ), true ) ? $r['lang'] : 'uk' ), array() );
				return array( 'count' => count( $m ) );
			},
		),
		array(
			'methods'             => 'POST',
			'permission_callback' => $perm,
			'callback'            => function ( $r ) {
				$lang = in_array( $r['lang'], array( 'ru', 'ar' ), true ) ? $r['lang'] : 'uk';
				$map  = array();
				foreach ( (array) $r['map'] as $en => $tr ) {
					$en = trim( preg_replace( '/\s+/', ' ', (string) $en ) );
					if ( '' !== $en ) {
						$map[ $en ] = str_replace( '<', '&lt;', (string) $tr );
					}
				}
				update_option( 'medlux_xlang_' . $lang, $map, false );
				return array( 'saved' => count( $map ), 'lang' => $lang );
			},
		),
	) );
	// same as Settings → Permalinks → Save (Site Health: "The authorisation header is invalid" → "Flush permalinks")
	register_rest_route( 'medlux/v1', '/flush-permalinks', array(
		'methods'             => 'POST',
		'permission_callback' => $perm,
		'callback'            => function () {
			require_once ABSPATH . 'wp-admin/includes/misc.php';
			require_once ABSPATH . 'wp-admin/includes/file.php';
			flush_rewrite_rules( true );
			return array( 'flushed' => true, 'htaccess_writable' => is_writable( get_home_path() . '.htaccess' ) );
		},
	) );
	// read-only: results of the WordPress "Site Health" checks that run inside the admin (Tools → Site Health)
	register_rest_route( 'medlux/v1', '/site-health', array(
		'methods'             => 'GET',
		'permission_callback' => $perm,
		'callback'            => function () {
			require_once ABSPATH . 'wp-admin/includes/admin.php';
			if ( ! class_exists( 'WP_Site_Health' ) ) {
				require_once ABSPATH . 'wp-admin/includes/class-wp-site-health.php';
			}
			$health = WP_Site_Health::get_instance();
			$out    = array();
			foreach ( WP_Site_Health::get_tests()['direct'] as $key => $test ) {
				$r = null;
				if ( is_string( $test['test'] ) && method_exists( $health, 'get_test_' . $test['test'] ) ) {
					$r = call_user_func( array( $health, 'get_test_' . $test['test'] ) );
				} elseif ( is_callable( $test['test'] ) ) {
					$r = call_user_func( $test['test'] );
				}
				if ( is_array( $r ) ) {
					$out[ $key ] = array( 'status' => $r['status'], 'label' => wp_strip_all_tags( $r['label'] ), 'description' => wp_strip_all_tags( $r['description'] ) );
				}
			}
			// who hooks into the update filters (Site Health: "security and maintenance releases are blocked")
			global $wp_filter;
			foreach ( array( 'allow_minor_auto_core_updates', 'auto_update_core', 'automatic_updater_disabled', 'auto_update_plugin' ) as $f ) {
				if ( empty( $wp_filter[ $f ] ) ) {
					continue;
				}
				foreach ( $wp_filter[ $f ]->callbacks as $prio => $cbs ) {
					foreach ( $cbs as $cb ) {
						try {
							$fn  = $cb['function'];
							$ref = is_array( $fn ) ? new ReflectionMethod( $fn[0], $fn[1] ) : new ReflectionFunction( $fn );
							$out['hooks'][ $f ][] = $prio . ' ' . str_replace( ABSPATH, '', (string) $ref->getFileName() ) . ':' . $ref->getStartLine();
						} catch ( Exception $e ) {
							$out['hooks'][ $f ][] = $prio . ' ' . ( is_string( $cb['function'] ) ? $cb['function'] : '?' );
						}
					}
				}
			}
			return $out;
		},
	) );
} );
