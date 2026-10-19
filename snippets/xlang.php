// MedLuxLife: Ukrainian (/uk/…), Russian (/ru/…) and Arabic (/ar/…, right to left) without extra TranslatePress languages (the free plugin allows English + 2: German, Turkish).
// /uk/<path> and /ru/<path> are served as the English page <path>. The finished HTML gets every text node and alt / placeholder / aria-label /
// title / submit label swapped from the list for that language (option medlux_xlang_<lang>, written by tools/xlang.py), internal links get the
// language prefix and <html lang> is set. Strings that are not in the list stay English. All pages get hreflang links for uk / ru / ar, and the
// header language list gets Українська / Русский / العربية.
if ( ! defined( 'MEDLUX_XLANG' ) ) {
	$medlux_xl  = '';
	$medlux_uri = isset( $_SERVER['REQUEST_URI'] ) ? (string) $_SERVER['REQUEST_URI'] : '';
	if ( preg_match( '#^/(uk|ru|ar)(?=/|\?|$)#', $medlux_uri, $medlux_m ) ) {
		$medlux_xl              = $medlux_m[1];
		$medlux_rest            = (string) substr( $medlux_uri, strlen( $medlux_m[0] ) );
		$_SERVER['REQUEST_URI'] = ( '' === $medlux_rest || '?' === $medlux_rest[0] ) ? '/' . $medlux_rest : $medlux_rest;
	}
	define( 'MEDLUX_XLANG', $medlux_xl );
}

// languages shown in the header list and in hreflang (a language is added here once its list is complete; its pages work before that for testing)
function medlux_xlang_live() {
	return array( 'uk', 'ru', 'ar' );
}

// https://medluxlife.de – scheme and host only: on /de/ and /tr/ pages TranslatePress adds its prefix to home_url(), get_option( 'home' ) and esc_url()
function medlux_xlang_home() {
	$u = wp_parse_url( get_option( 'home' ) );
	return ( isset( $u['scheme'] ) ? $u['scheme'] : 'https' ) . '://' . $u['host'];
}

function medlux_xlang_map() {
	static $map = null;
	if ( null === $map ) {
		$map = MEDLUX_XLANG ? (array) get_option( 'medlux_xlang_' . MEDLUX_XLANG, array() ) : array();
	}
	return $map;
}

// path of the current page without a language prefix, e.g. /health/clinical-treatments/
function medlux_xlang_path() {
	$path = '/';
	if ( is_singular() && ! is_front_page() ) {
		$path = (string) wp_parse_url( get_permalink( get_queried_object_id() ), PHP_URL_PATH );
	}
	return preg_replace( '#^/(en|de|tr|uk|ru|ar)(?=/)#', '', $path );
}

function medlux_xlang_render( $html ) {
	if ( '' === MEDLUX_XLANG || false === stripos( $html, '<html' ) ) {
		return $html;
	}
	$map  = medlux_xlang_map();
	$lang = MEDLUX_XLANG;
	$home = medlux_xlang_home();
	// scripts, styles, form fields and the hreflang links stay as they are
	$keep = array();
	$html = preg_replace_callback( '#<(script|style|textarea)\b[^>]*>.*?</\1>|<link\b[^>]*\bhreflang=[^>]*>#is', function ( $m ) use ( &$keep ) {
		$keep[] = $m[0];
		return '<!--mlxkeep' . ( count( $keep ) - 1 ) . '-->';
	}, $html );
	if ( $map ) {
		$html = preg_replace_callback( '/>([^<>]+)</', function ( $m ) use ( $map ) {
			$k = trim( preg_replace( '/\s+/', ' ', $m[1] ) );
			if ( '' === $k || ! isset( $map[ $k ] ) ) {
				return $m[0];
			}
			$lead = preg_match( '/^\s+/', $m[1], $a ) ? $a[0] : '';
			$tail = preg_match( '/\s+$/', $m[1], $b ) ? $b[0] : '';
			return '>' . $lead . $map[ $k ] . $tail . '<';
		}, $html );
		$attr = function ( $m ) use ( $map ) {
			$k = trim( preg_replace( '/\s+/', ' ', $m[2] ) );
			return isset( $map[ $k ] ) ? $m[1] . '"' . esc_attr( html_entity_decode( $map[ $k ], ENT_QUOTES, 'UTF-8' ) ) . '"' : $m[0];
		};
		$html = preg_replace_callback( '/(\b(?:alt|placeholder|aria-label|title)=)"([^"]*)"/', $attr, $html );
		$html = preg_replace_callback( '/(<input\b[^>]*\btype="submit"[^>]*\bvalue=)"([^"]*)"/', $attr, $html );
	}
	// internal page links and the canonical / og:url get the language prefix
	$q    = preg_quote( $home, '#' );
	$link = function ( $m ) use ( $lang ) {
		$p = isset( $m[3] ) ? $m[3] : '';
		$p = '' === $p ? '/' : $p;
		if ( preg_match( '#^/(wp-|de/|tr/|uk/|ru/|ar/|feed|xmlrpc|comments)#', $p ) || preg_match( '#\.(jpe?g|png|webp|gif|svg|pdf|css|js|xml|ico|woff2?)(\?|$)#i', $p ) ) {
			return $m[0];
		}
		return $m[1] . $m[2] . '/' . $lang . $p . '"';
	};
	$html = preg_replace_callback( '#(\bhref=")(' . $q . ')(/[^"]*)?"#', $link, $html );
	$html = preg_replace_callback( '#(<meta property="og:url" content=")(' . $q . ')(/[^"]*)?"#', $link, $html );
	$html = preg_replace( '/<html([^>]*)\slang="[^"]*"/', '<html$1 lang="' . $lang . '"', $html, 1 );
	// the contact form box carries the language and direction of the English page
	$html = preg_replace_callback( '/<div class="wpcf7\b[^>]*>/', function ( $m ) use ( $lang ) {
		$tag = preg_replace( '/\slang="[^"]*"/', ' lang="' . $lang . '"', $m[0] );
		return preg_replace( '/\sdir="[^"]*"/', ' dir="' . ( 'ar' === $lang ? 'rtl' : 'ltr' ) . '"', $tag );
	}, $html );
	if ( 'ar' === $lang && ! preg_match( '/<html[^>]*\sdir=/', $html ) ) {
		$html = preg_replace( '/<html\b/', '<html dir="rtl"', $html, 1 );
	}
	foreach ( $keep as $i => $k ) {
		$html = str_replace( '<!--mlxkeep' . $i . '-->', $k, $html );
	}
	return $html;
}

// Arabic is written right to left: WordPress then loads the right-to-left versions of its styles and writes dir="rtl"
if ( 'ar' === MEDLUX_XLANG ) {
	add_action( 'after_setup_theme', function () {
		if ( isset( $GLOBALS['wp_locale'] ) ) {
			$GLOBALS['wp_locale']->text_direction = 'rtl';
		}
	}, 0 );
	add_action( 'wp_enqueue_scripts', function () {
		wp_styles()->text_direction = 'rtl';
	}, 0 );
}

if ( MEDLUX_XLANG ) {
	add_action( 'template_redirect', function () {
		ob_start( 'medlux_xlang_render' );
	}, -1000 );
}


// hreflang for the Ukrainian and Russian versions on every page (TranslatePress lists en / de / tr itself)
add_action( 'wp_head', function () {
	if ( is_404() || is_search() ) {
		return;
	}
	$path = medlux_xlang_path();
	foreach ( medlux_xlang_live() as $l ) {
		printf( '<link rel="alternate" hreflang="%s" href="%s" />' . "\n", esc_attr( $l ), esc_attr( medlux_xlang_home() . '/' . $l . $path ) );
	}
}, 2 );

// header language list: Українська / Русский on every page; on /uk/ and /ru/ the current language and English are set right
add_action( 'wp_footer', function () {
	$flags = plugins_url( 'translatepress-multilingual/assets/flags/4x3/' );
	$cfg   = array(
		'cur'   => MEDLUX_XLANG,
		'live'  => medlux_xlang_live(),
		'path'  => medlux_xlang_path(),
		'home'  => medlux_xlang_home(),
		'items' => array(
			'uk' => array( 'name' => 'Українська', 'flag' => $flags . 'uk.svg' ),
			'ru' => array( 'name' => 'Русский', 'flag' => $flags . 'ru_RU.svg' ),
			'ar' => array( 'name' => 'العربية', 'flag' => $flags . 'ar.svg' ),
			'en' => array( 'name' => 'English', 'flag' => $flags . 'en_GB.svg' ),
		),
		'cf7'   => array(),
	);
	// texts that scripts put into the page after it is loaded, so they are not in the HTML: contact form messages, a few labels
	$cf7 = array(
		'uk' => array(
			'Thank you for your message. It has been sent.' => 'Дякуємо за ваше повідомлення. Його надіслано.',
			'There was an error trying to send your message. Please try again later.' => 'Під час надсилання повідомлення сталася помилка. Будь ласка, спробуйте пізніше.',
			'One or more fields have an error. Please check and try again.' => 'В одному або кількох полях є помилка. Будь ласка, перевірте та спробуйте ще раз.',
			'You must accept the terms and conditions before sending your message.' => 'Перед надсиланням повідомлення потрібно прийняти умови.',
			'Please fill out this field.' => 'Будь ласка, заповніть це поле.',
			'This field has a too long input.' => 'Текст у цьому полі задовгий.',
			'Please enter an email address.' => 'Будь ласка, введіть адресу електронної пошти.',
			'Please enter a telephone number.' => 'Будь ласка, введіть номер телефону.',
			// labels set by scripts (search button, logo)
			'Expand search field' => 'Відкрити поле пошуку',
			'Submit Search' => 'Шукати',
			'Site Logo' => 'Логотип сайту',
		),
		'ru' => array(
			'Thank you for your message. It has been sent.' => 'Спасибо за ваше сообщение. Оно отправлено.',
			'There was an error trying to send your message. Please try again later.' => 'При отправке сообщения произошла ошибка. Пожалуйста, попробуйте позже.',
			'One or more fields have an error. Please check and try again.' => 'В одном или нескольких полях есть ошибка. Пожалуйста, проверьте и попробуйте ещё раз.',
			'You must accept the terms and conditions before sending your message.' => 'Перед отправкой сообщения необходимо принять условия.',
			'Please fill out this field.' => 'Пожалуйста, заполните это поле.',
			'This field has a too long input.' => 'Текст в этом поле слишком длинный.',
			'Please enter an email address.' => 'Пожалуйста, введите адрес электронной почты.',
			'Please enter a telephone number.' => 'Пожалуйста, введите номер телефона.',
			// labels set by scripts (search button, logo)
			'Expand search field' => 'Открыть поле поиска',
			'Submit Search' => 'Искать',
			'Site Logo' => 'Логотип сайта',
		),
		'ar' => array(
			'Thank you for your message. It has been sent.' => 'شكرًا لرسالتكم. تم إرسالها.',
			'There was an error trying to send your message. Please try again later.' => 'حدث خطأ أثناء إرسال رسالتكم. يُرجى المحاولة مرة أخرى لاحقًا.',
			'One or more fields have an error. Please check and try again.' => 'يوجد خطأ في حقل واحد أو أكثر. يُرجى التحقق والمحاولة مرة أخرى.',
			'You must accept the terms and conditions before sending your message.' => 'يجب الموافقة على الشروط والأحكام قبل إرسال رسالتكم.',
			'Please fill out this field.' => 'يُرجى ملء هذا الحقل.',
			'This field has a too long input.' => 'النص في هذا الحقل طويل جدًا.',
			'Please enter an email address.' => 'يُرجى إدخال عنوان بريد إلكتروني.',
			'Please enter a telephone number.' => 'يُرجى إدخال رقم هاتف.',
			// labels set by scripts (search button, logo)
			'Expand search field' => 'فتح حقل البحث',
			'Submit Search' => 'بحث',
			'Site Logo' => 'شعار الموقع',
		),
	);
	if ( MEDLUX_XLANG && isset( $cf7[ MEDLUX_XLANG ] ) ) {
		$cfg['cf7'] = $cf7[ MEDLUX_XLANG ];
	}
	?>
<script>
(function (C) {
  function item(code) {
    var it = C.items[code], a = document.createElement('a');
    a.className = 'trp-language-item mlx-xlang-item';
    a.href = C.home + (code === 'en' ? '' : '/' + code) + C.path;
    a.setAttribute('title', it.name);
    a.innerHTML = '<img class="trp-flag-image" src="' + it.flag + '" alt="" role="presentation"> <span class="trp-language-item-name" data-no-translation>' + it.name + '</span>';
    return a;
  }
  document.querySelectorAll('.trp-shortcode-switcher').forEach(function (sw) {
    var list = sw.querySelector('.trp-switcher-dropdown-list');
    if (C.cur) {
      // current language: Ukrainian / Russian instead of English
      sw.querySelectorAll('.trp-language-item__current').forEach(function (cur) {
        var img = cur.querySelector('img'), nm = cur.querySelector('.trp-language-item-name');
        if (img) img.src = C.items[C.cur].flag;
        if (nm) nm.textContent = C.items[C.cur].name;
        cur.setAttribute('title', C.items[C.cur].name);
      });
      if (list) list.insertBefore(item('en'), list.firstChild);
    }
    if (list) C.live.forEach(function (c) { if (c !== C.cur) list.appendChild(item(c)); });
  });
  if (C.cur) {
    var fix = function () {
      document.querySelectorAll('.wpcf7-response-output, .wpcf7-not-valid-tip').forEach(function (el) {
        var t = el.textContent.trim();
        if (C.cf7[t]) el.textContent = C.cf7[t];
      });
      document.querySelectorAll('[aria-label], img[alt]').forEach(function (el) {
        ['aria-label', 'alt'].forEach(function (a) { var v = el.getAttribute(a); if (v && C.cf7[v]) el.setAttribute(a, C.cf7[v]); });
      });
    };
    fix();
    var queued = false;
    new MutationObserver(function () { if (!queued) { queued = true; requestAnimationFrame(function () { queued = false; fix(); }); } }).observe(document.body, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ['aria-label', 'alt'] });
    window.addEventListener('load', fix);
  }
})(<?php echo wp_json_encode( $cfg ); ?>);
</script>
	<?php
}, 50 );
