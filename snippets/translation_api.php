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
				'rows'  => $wpdb->get_results( "SELECT id, original, translated, status, block_type FROM `$t` WHERE $where ORDER BY id LIMIT $offset, $limit", ARRAY_A ),
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
} );
