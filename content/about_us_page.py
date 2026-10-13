"""About Us (page 24) content: text approved by the owner on 2026-10-13 (content/about_us_draft.md).
EN/DE/TR via TranslatePress [trp_language] shortcodes. Builds the block markup and prints it."""
def t(en, de, tr):
    return (f'[trp_language language="en_GB"]{en}[/trp_language]'
            f'[trp_language language="de_DE"]{de}[/trp_language]'
            f'[trp_language language="tr_TR"]{tr}[/trp_language]')

SLOGAN = t('Expert medical care and tailored travel — we manage every detail from day one so your journey is completely seamless.',
           'Fachkundige medizinische Versorgung und maßgeschneiderte Reisen — wir kümmern uns vom ersten Tag an um jedes Detail, damit Ihre Reise absolut reibungslos verläuft.',
           'Uzman tıbbi bakım ve kişiye özel seyahat — yolculuğunuzun kusursuz geçmesi için ilk günden itibaren her detayla biz ilgileniyoruz.')
INTRO = t('At MedLuxLife, based in Aachen, Germany, we believe that true comfort means not having to worry about the details. We offer an end-to-end service and organise everything from A to Z, so you can focus on what matters to you.',
          'MedLuxLife mit Sitz in Aachen steht für einen Gedanken: Wahrer Komfort bedeutet, sich um die Einzelheiten keine Sorgen machen zu müssen. Wir bieten Ihnen einen Rundum-Service und organisieren alles von A bis Z – damit Sie sich auf das konzentrieren können, was Ihnen wichtig ist.',
          "Almanya'nın Aachen şehrinde bulunan MedLuxLife olarak, gerçek konforun ayrıntılar için endişelenmemek olduğuna inanıyoruz. Size uçtan uca bir hizmet sunuyor, her şeyi A'dan Z'ye organize ediyoruz; böylece siz sizin için önemli olana odaklanabilirsiniz.")
HEALTH_H = t('Health', 'Gesundheit', 'Sağlık')
HEALTH = t('We take a personal approach to your health journey. We listen carefully to your needs and wishes, pass your medical records on to experienced specialists at carefully selected partner clinics and hospitals for review, and arrange your consultations. From the first contact and the treatment plan prepared by the doctors to appointments, translations and travel logistics, we coordinate every step with care.',
           'Wir begleiten Sie persönlich und individuell. Wir hören Ihnen genau zu, leiten Ihre medizinischen Unterlagen zur Prüfung an erfahrene Fachärztinnen und Fachärzte in sorgfältig ausgewählten Partnerkliniken und -krankenhäusern weiter und vereinbaren Ihre Konsultationen. Vom ersten Kontakt über den ärztlichen Behandlungsplan bis zu Terminen, Übersetzungen und der Reiseorganisation koordinieren wir jeden Schritt mit Sorgfalt.',
           'Sağlık yolculuğunuzda size kişisel ve özel bir yaklaşımla eşlik ediyoruz. İhtiyaçlarınızı ve isteklerinizi dikkatle dinliyor, tıbbi belgelerinizi incelenmek üzere özenle seçilmiş partner klinik ve hastanelerdeki deneyimli uzman hekimlere iletiyor ve görüşmelerinizi ayarlıyoruz. İlk temastan hekimlerin hazırladığı tedavi planına, randevulardan tercümelere ve seyahat organizasyonuna kadar her adımı özenle koordine ediyoruz.')
TRAVEL_H = t('Travel', 'Reisen', 'Seyahat')
TRAVEL = t('We put together journeys tailored to your personal preferences and budget. Whether you are looking for a restful holiday, a city break or a pilgrimage, we take care of the organisation — from flights and private transfers to hand-picked hotels — so you can simply enjoy your trip.',
           'Wir stellen Reisen ganz nach Ihren persönlichen Wünschen und Ihrem Budget zusammen. Ob erholsamer Urlaub, Städtereise oder Pilgerreise – wir übernehmen die Organisation, von Flügen und privaten Transfers bis zu ausgewählten Hotels, damit Sie Ihre Reise einfach genießen können.',
           'Kişisel tercihlerinize ve bütçenize göre size özel seyahatler hazırlıyoruz. İster dinlendirici bir tatil, ister bir şehir gezisi, ister bir hac/umre yolculuğu olsun; uçuşlardan özel transferlere ve özenle seçilmiş otellere kadar tüm organizasyonu üstleniyoruz, siz de yolculuğunuzun tadını çıkarın.')
PARTNERS_H = t('Our partners in Istanbul', 'Unsere Partner in Istanbul', "İstanbul'daki partnerlerimiz")
PARTNERS = t('For hospital and specialist treatments, we work with a large university hospital group in Istanbul with several hospitals and specialised centres, academic specialists in almost every field, modern diagnostics such as 3-Tesla MRI and PET-CT, and international JCI accreditation. For aesthetic, hair and dental treatments, we work with a specialised clinic in Istanbul that focuses on caring for international patients. We plan to add further renowned hospitals to our network, always selected by the same criteria: medical quality, transparency and genuine care for international patients.',
             'Für Krankenhaus- und Facharztbehandlungen arbeiten wir mit einer großen Universitätsklinik-Gruppe in Istanbul zusammen – mit mehreren Krankenhäusern und spezialisierten Zentren, akademischen Fachärztinnen und Fachärzten aus nahezu allen Fachgebieten, moderner Diagnostik wie 3-Tesla-MRT und PET-CT sowie internationaler JCI-Akkreditierung. Für ästhetische Behandlungen, Haar- und Zahnbehandlungen arbeiten wir mit einer spezialisierten Klinik in Istanbul zusammen, die sich auf die Betreuung internationaler Patientinnen und Patienten konzentriert. Wir möchten unser Netzwerk künftig um weitere renommierte Krankenhäuser erweitern – stets nach denselben Kriterien ausgewählt: medizinische Qualität, Transparenz und echte Fürsorge für internationale Patientinnen und Patienten.',
             "Hastane ve uzman tedavileri için İstanbul'da büyük bir üniversite hastaneleri grubuyla çalışıyoruz: birden fazla hastane ve uzmanlaşmış merkez, neredeyse her alanda akademik uzman hekimler, 3 Tesla MR ve PET-BT gibi modern tanı imkânları ve uluslararası JCI akreditasyonu. Estetik, saç ve diş tedavileri için ise İstanbul'da uluslararası hastaların bakımına odaklanan uzman bir klinikle çalışıyoruz. Ağımıza ileride başka tanınmış hastaneleri de eklemeyi planlıyoruz; her zaman aynı kriterlere göre seçerek: tıbbi kalite, şeffaflık ve uluslararası hastalara gerçek ilgi.")
LANG_H = t('We speak your language', 'Wir sprechen Ihre Sprache', 'Sizin dilinizi konuşuyoruz')
LANG = t('Our team speaks Turkish, Ukrainian, Russian, English and German, so you can talk to us in the language you feel most comfortable with. At our partner clinics and hospital, native-speaking interpreters for English, German, French, Italian, Spanish, Arabic, Turkish, Russian and Ukrainian are available whenever you need them.',
         'Unser Team spricht Türkisch, Ukrainisch, Russisch, Englisch und Deutsch – so können Sie mit uns in der Sprache sprechen, in der Sie sich am wohlsten fühlen. In unseren Partnerkliniken und unserem Partnerkrankenhaus stehen Ihnen bei Bedarf muttersprachliche Dolmetscherinnen und Dolmetscher für Englisch, Deutsch, Französisch, Italienisch, Spanisch, Arabisch, Türkisch, Russisch und Ukrainisch zur Verfügung.',
         'Ekibimiz Türkçe, Ukraynaca, Rusça, İngilizce ve Almanca konuşuyor; böylece bizimle kendinizi en rahat hissettiğiniz dilde konuşabilirsiniz. Partner klinik ve hastanemizde İngilizce, Almanca, Fransızca, İtalyanca, İspanyolca, Arapça, Türkçe, Rusça ve Ukraynaca için anadili düzeyinde tercümanlar ihtiyaç duyduğunuz her an hazırdır.')
CTA_H = t('We are here for you', 'Wir sind für Sie da', 'Sizin için buradayız')
CTA = t("You don't need to think about the organisation. You reach out to us, and from that moment on we take care of it for you.",
        'Sie müssen sich um die Organisation nicht kümmern. Sie nehmen Kontakt mit uns auf – und ab diesem Moment übernehmen wir das für Sie.',
        'Organizasyonu düşünmenize gerek yok. Bize ulaşmanız yeterli — o andan itibaren her şeyi sizin için biz üstleniyoruz.')
BTN = t('Request a Free Consultation', 'Kostenlose Beratung anfragen', 'Ücretsiz Danışmanlık Talep Edin')
NOTE = t('Please note: MedLuxLife does not provide medical treatment itself. Medical services are provided exclusively by licensed doctors and clinics; we act as an intermediary and coordinator. For travel services, we act as an intermediary between you and the respective airlines, hotels and transfer providers.',
         'Hinweis: MedLuxLife erbringt selbst keine medizinischen Leistungen. Medizinische Leistungen werden ausschließlich von zugelassenen Ärztinnen, Ärzten und Kliniken erbracht; wir sind als Vermittler und Koordinator tätig. Bei Reiseleistungen handeln wir als Vermittler zwischen Ihnen und den jeweiligen Fluggesellschaften, Hotels und Transferunternehmen.',
         'Not: MedLuxLife kendisi tıbbi hizmet sunmaz. Tıbbi hizmetler yalnızca yetkili hekimler ve klinikler tarafından verilir; biz aracı ve koordinatör olarak çalışırız. Seyahat hizmetlerinde ise sizinle ilgili havayolu şirketleri, oteller ve transfer firmaları arasında aracılık yaparız.')
IMG = ('https://medluxlife.de/wp-content/uploads/2026/09/f28c2283b05e8a5909e33617ef555e2f8d51c8dc-1024x683.jpg', 37,
       'Bright, modern lounge with curved sofas and large windows')
WHATSAPP = 'https://wa.me/380979092326'
B = 'https://medluxlife.de'

def card(h, p):
    return (f'<!-- wp:group {{"className":"medlux-card","layout":{{"type":"constrained"}}}} -->\n<div class="wp-block-group medlux-card"><!-- wp:heading {{"level":3}} -->\n'
            f'<h3 class="wp-block-heading">{h}</h3>\n<!-- /wp:heading -->\n\n<!-- wp:paragraph -->\n<p>{p}</p>\n<!-- /wp:paragraph --></div>\n<!-- /wp:group -->')

def build():
    src, mid, alt = IMG
    return f'''<!-- wp:columns {{"verticalAlignment":"center","className":"medlux-intro"}} -->
<div class="wp-block-columns are-vertically-aligned-center medlux-intro"><!-- wp:column {{"verticalAlignment":"center"}} -->
<div class="wp-block-column is-vertically-aligned-center"><!-- wp:paragraph {{"className":"medlux-about-slogan"}} -->
<p class="medlux-about-slogan">{SLOGAN}</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph {{"className":"medlux-lead"}} -->
<p class="medlux-lead">{INTRO}</p>
<!-- /wp:paragraph --></div>
<!-- /wp:column -->

<!-- wp:column {{"verticalAlignment":"center"}} -->
<div class="wp-block-column is-vertically-aligned-center"><!-- wp:image {{"id":{mid},"sizeSlug":"large","linkDestination":"none","className":"medlux-intro-img"}} -->
<figure class="wp-block-image size-large medlux-intro-img"><img src="{src}" alt="{alt}" class="wp-image-{mid}"/></figure>
<!-- /wp:image --></div>
<!-- /wp:column --></div>
<!-- /wp:columns -->

<!-- wp:group {{"className":"medlux-section","layout":{{"type":"constrained"}}}} -->
<div class="wp-block-group medlux-section"><!-- wp:group {{"className":"medlux-treatment-grid","layout":{{"type":"grid","minimumColumnWidth":"20rem"}}}} -->
<div class="wp-block-group medlux-treatment-grid">{card(HEALTH_H, HEALTH)}

{card(TRAVEL_H, TRAVEL)}</div>
<!-- /wp:group -->

{card(PARTNERS_H, PARTNERS).replace('"className":"medlux-card"', '"className":"medlux-card medlux-card-wide"', 1).replace('class="wp-block-group medlux-card"', 'class="wp-block-group medlux-card medlux-card-wide"', 1)}

{card(LANG_H, LANG).replace('"className":"medlux-card"', '"className":"medlux-card medlux-card-wide"', 1).replace('class="wp-block-group medlux-card"', 'class="wp-block-group medlux-card medlux-card-wide"', 1)}</div>
<!-- /wp:group -->

<!-- wp:group {{"className":"medlux-cta","layout":{{"type":"constrained"}}}} -->
<div class="wp-block-group medlux-cta"><!-- wp:heading -->
<h2 class="wp-block-heading">{CTA_H}</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>{CTA}</p>
<!-- /wp:paragraph -->

<!-- wp:buttons -->
<div class="wp-block-buttons"><!-- wp:button {{"className":"medlux-btn-primary"}} -->
<div class="wp-block-button medlux-btn-primary"><a class="wp-block-button__link wp-element-button" href="{B}/contact/">{BTN}</a></div>
<!-- /wp:button --><!-- wp:button {{"className":"medlux-btn-whatsapp"}} -->
<div class="wp-block-button medlux-btn-whatsapp"><a class="wp-block-button__link wp-element-button" href="{WHATSAPP}" target="_blank" rel="noreferrer noopener">WhatsApp</a></div>
<!-- /wp:button --></div>
<!-- /wp:buttons -->

<!-- wp:paragraph {{"className":"medlux-disclaimer"}} -->
<p class="medlux-disclaimer">{NOTE}</p>
<!-- /wp:paragraph --></div>
<!-- /wp:group -->'''

if __name__ == '__main__':
    print(build())
