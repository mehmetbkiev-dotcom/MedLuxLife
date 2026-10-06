"""Datenschutzerklärung (page 3, /privacy-policy/) and AGB (/terms/) for MedLuxLife.

Written in German (binding version). Values in PH(...) are placeholders that must be
filled in before launch (legal entity, address, representative).
"""
import json, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from blocks import p, h, ul, group, B

def PH(t): return f'<mark class="medlux-placeholder">[{t}]</mark>'

COMPANY = "Inh. Anna Sacilanates (Einzelunternehmen)"
ADDRESS = f"Stolberger Straße {PH('Hausnummer')}, 52068 Aachen, Deutschland"
CONTACT = f'Telefon: <a href="tel:+4916093448714">+49 160 93 44 87 14</a><br>E-Mail: <a href="mailto:info@medluxlife.com">info@medluxlife.com</a>'
DATE = "Oktober 2026"

def note():
    return p('<em>This document is provided in German, which is the legally binding version. Translations into other languages are provided for convenience only.</em>', "medlux-legal-note")

def privacy():
    b = [note(), p(f"Stand: {DATE}")]
    b += [h("1. Verantwortlicher"),
          p("Verantwortlich für die Verarbeitung personenbezogener Daten auf dieser Website im Sinne der Datenschutz-Grundverordnung (DSGVO) ist:"),
          p(f"MedLuxLife<br>{COMPANY}<br>{ADDRESS}<br>{CONTACT}"),
          p("Bei Fragen zum Datenschutz können Sie sich jederzeit unter den oben genannten Kontaktdaten an uns wenden.")]
    b += [h("2. Überblick"),
          p("Wir verarbeiten personenbezogene Daten nur, soweit dies zur Bereitstellung einer funktionsfähigen Website sowie zur Beantwortung Ihrer Anfragen und zur Erbringung unserer Leistungen erforderlich ist. Auf dieser Website setzen wir derzeit <strong>keine Analyse-, Tracking- oder Marketing-Tools</strong> ein und binden keine Social-Media-Plugins ein."),
          p("Rechtsgrundlagen der Verarbeitung sind insbesondere:"),
          ul(["Art. 6 Abs. 1 lit. a DSGVO (Einwilligung),",
              "Art. 6 Abs. 1 lit. b DSGVO (Vertragserfüllung und vorvertragliche Maßnahmen),",
              "Art. 6 Abs. 1 lit. c DSGVO (rechtliche Verpflichtung, z. B. handels- und steuerrechtliche Aufbewahrungspflichten),",
              "Art. 6 Abs. 1 lit. f DSGVO (berechtigte Interessen),",
              "Art. 9 Abs. 2 lit. a DSGVO (ausdrückliche Einwilligung bei Gesundheitsdaten)."])]
    b += [h("3. Hosting und Server-Logfiles"),
          p("Diese Website wird bei der IONOS SE, Elgendorfer Str. 57, 56410 Montabaur, Deutschland, gehostet. Mit IONOS besteht ein Vertrag zur Auftragsverarbeitung gemäß Art. 28 DSGVO. Die Server befinden sich in der Europäischen Union."),
          p("Beim Aufruf der Website werden durch den Server automatisch Informationen erfasst, die Ihr Browser übermittelt (Server-Logfiles):"),
          ul(["IP-Adresse (gekürzt bzw. nur kurzzeitig gespeichert)", "Datum und Uhrzeit des Zugriffs", "aufgerufene Seite bzw. Datei", "Referrer-URL", "Browsertyp und -version, Betriebssystem"]),
          p("Die Verarbeitung erfolgt auf Grundlage von Art. 6 Abs. 1 lit. f DSGVO. Unser berechtigtes Interesse liegt in der sicheren und stabilen Bereitstellung der Website sowie in der Abwehr von Angriffen. Die Logfiles werden nach kurzer Zeit, spätestens nach den Vorgaben des Hosters, gelöscht.")]
    b += [h("4. SSL-/TLS-Verschlüsselung"),
          p("Diese Website nutzt aus Sicherheitsgründen eine SSL- bzw. TLS-Verschlüsselung. Eine verschlüsselte Verbindung erkennen Sie an „https://“ in der Adresszeile Ihres Browsers.")]
    b += [h("5. Cookies und Spracheinstellung"),
          p("Wir verwenden ausschließlich technisch notwendige Cookies bzw. vergleichbare Technologien, die für den Betrieb der Website erforderlich sind, z. B. um die von Ihnen gewählte Sprache zu speichern (Sprachumschalter). Rechtsgrundlage ist § 25 Abs. 2 Nr. 2 TDDDG sowie Art. 6 Abs. 1 lit. f DSGVO. Cookies zu Analyse- oder Werbezwecken setzen wir nicht ein. Sie können Cookies in Ihren Browsereinstellungen jederzeit löschen oder blockieren.")]
    b += [h("6. Kontaktformular"),
          p("Wenn Sie uns über das Kontaktformular eine Anfrage senden, verarbeiten wir die von Ihnen angegebenen Daten: Name, E-Mail-Adresse, Telefonnummer (freiwillig), gewünschter Bereich (Health oder Travel) und Ihre Nachricht. Die Angaben werden per E-Mail an uns übermittelt und zur Bearbeitung Ihrer Anfrage verwendet."),
          p("Rechtsgrundlage ist Art. 6 Abs. 1 lit. b DSGVO, soweit Ihre Anfrage auf den Abschluss oder die Durchführung eines Vertrags gerichtet ist, im Übrigen Ihre Einwilligung nach Art. 6 Abs. 1 lit. a DSGVO, die Sie durch Anklicken des Kontrollkästchens erteilen. Sie können Ihre Einwilligung jederzeit mit Wirkung für die Zukunft widerrufen."),
          p("Bitte senden Sie uns über das Kontaktformular <strong>keine ausführlichen medizinischen Informationen oder Unterlagen</strong>. Sofern solche Daten für Ihre Anfrage erforderlich werden, fordern wir sie gesondert und auf sicherem Weg an."),
          p("Für das Formular nutzen wir das WordPress-Plugin „Contact Form 7“. Die Formulardaten werden nicht in einer Datenbank auf der Website gespeichert, sondern ausschließlich per E-Mail an uns weitergeleitet.")]
    b += [h("7. Kontakt per E-Mail, Telefon und WhatsApp"),
          p("Wenn Sie uns per E-Mail oder Telefon kontaktieren, verarbeiten wir Ihre Angaben zur Bearbeitung Ihres Anliegens (Art. 6 Abs. 1 lit. b bzw. lit. f DSGVO)."),
          p("Auf unserer Website verlinken wir auf WhatsApp. Es handelt sich um einen einfachen Link; beim bloßen Besuch unserer Website werden keine Daten an WhatsApp übertragen. Erst wenn Sie den Link anklicken und uns über WhatsApp schreiben, werden Ihre Daten (u. a. Telefonnummer, Profilname, Nachrichteninhalte, Metadaten) von der WhatsApp Ireland Limited, Merrion Road, Dublin 4, D04 X2K5, Irland, verarbeitet. Dabei kann eine Übermittlung an die Meta Platforms, Inc. in den USA stattfinden; das Unternehmen ist nach dem EU-U.S. Data Privacy Framework zertifiziert. Die Nutzung von WhatsApp ist freiwillig; Sie können uns jederzeit auch per E-Mail oder Telefon erreichen. Rechtsgrundlage ist Art. 6 Abs. 1 lit. a und lit. b DSGVO. Weitere Informationen finden Sie in der Datenschutzrichtlinie von WhatsApp."),
          p("Bitte senden Sie uns über WhatsApp keine Gesundheitsdaten oder medizinischen Unterlagen, sofern wir Sie nicht ausdrücklich darum bitten.")]
    b += [h("8. Verarbeitung im Rahmen unserer Leistungen"),
          h("Gesundheitsleistungen (Health)", 3),
          p("Wenn Sie unsere Unterstützung bei der Organisation einer medizinischen Behandlung in Anspruch nehmen, kann die Verarbeitung von Gesundheitsdaten (z. B. Befunde, Röntgenbilder, Angaben zu Vorerkrankungen) erforderlich sein. Diese besonderen Kategorien personenbezogener Daten verarbeiten wir ausschließlich auf Grundlage Ihrer <strong>ausdrücklichen Einwilligung</strong> gemäß Art. 9 Abs. 2 lit. a DSGVO, die wir gesondert einholen."),
          p("Zur Erstellung eines Behandlungsplans und zur Terminplanung übermitteln wir die erforderlichen Daten an unsere Partnerklinik bzw. die behandelnden Ärztinnen und Ärzte. Diese befinden sich in der Türkei und damit in einem Drittland, für das kein Angemessenheitsbeschluss der EU-Kommission besteht. Die Übermittlung erfolgt auf Grundlage Ihrer ausdrücklichen Einwilligung (Art. 49 Abs. 1 lit. a DSGVO) bzw. weil sie zur Erfüllung des in Ihrem Interesse geschlossenen Vertrags erforderlich ist (Art. 49 Abs. 1 lit. b und c DSGVO). Wir weisen darauf hin, dass im Drittland möglicherweise kein dem EU-Recht gleichwertiges Datenschutzniveau besteht und die Durchsetzung Ihrer Rechte erschwert sein kann. Die Partnerklinik ist für die Verarbeitung im Rahmen der Behandlung eigenständig verantwortlich."),
          h("Reiseleistungen (Travel)", 3),
          p("Für die Vermittlung von Hotels, Flügen, Transfers, Reisepaketen sowie Hajj- und Umrah-Reisen übermitteln wir die erforderlichen Daten (z. B. Name, Geburtsdatum, Reisepassdaten, Kontaktdaten, Reisedaten) an die jeweiligen Leistungsträger wie Hotels, Fluggesellschaften, Transferunternehmen und Reiseveranstalter. Rechtsgrundlage ist Art. 6 Abs. 1 lit. b DSGVO. Befindet sich ein Leistungsträger außerhalb der EU bzw. des EWR (z. B. in der Türkei oder in Saudi-Arabien), erfolgt die Übermittlung, weil sie zur Erfüllung des Vertrags erforderlich ist (Art. 49 Abs. 1 lit. b und c DSGVO). Für Hajj- und Umrah-Reisen können zudem Daten für Visa- und Einreiseverfahren an die zuständigen Stellen übermittelt werden, soweit dies erforderlich ist.")]
    b += [h("9. Empfänger personenbezogener Daten"),
          p("Ihre Daten erhalten innerhalb unseres Unternehmens nur die Personen, die sie zur Bearbeitung Ihres Anliegens benötigen. Externe Empfänger sind insbesondere unser Hosting- und E-Mail-Dienstleister (IONOS SE), die oben genannten Partnerkliniken und Leistungsträger sowie – soweit gesetzlich vorgeschrieben – Behörden und Steuerberater. Eine Weitergabe zu Werbezwecken findet nicht statt.")]
    b += [h("10. Links zu sozialen Netzwerken"),
          p("Auf unserer Website befinden sich einfache Links zu unseren Profilen bei Facebook, Instagram und X. Es werden keine Plugins eingebunden; Daten werden erst übertragen, wenn Sie einen Link anklicken und die Seite des jeweiligen Anbieters aufrufen. Dort gelten die Datenschutzbestimmungen des jeweiligen Anbieters.")]
    b += [h("11. Speicherdauer"),
          p("Wir speichern personenbezogene Daten nur so lange, wie es für den jeweiligen Zweck erforderlich ist. Anfragen, aus denen kein Vertrag entsteht, löschen wir in der Regel spätestens sechs Monate nach Abschluss der Kommunikation. Daten im Zusammenhang mit Verträgen speichern wir für die Dauer der Vertragsbeziehung und darüber hinaus, soweit gesetzliche Aufbewahrungsfristen bestehen (in der Regel sechs bzw. zehn Jahre nach HGB und AO). Gesundheitsdaten löschen wir, sobald sie für die Organisation der Behandlung nicht mehr benötigt werden oder Sie Ihre Einwilligung widerrufen, soweit keine gesetzlichen Pflichten entgegenstehen.")]
    b += [h("12. Ihre Rechte"),
          p("Sie haben im Rahmen der gesetzlichen Vorgaben jederzeit folgende Rechte:"),
          ul(["Auskunft über Ihre gespeicherten Daten (Art. 15 DSGVO)",
              "Berichtigung unrichtiger Daten (Art. 16 DSGVO)",
              "Löschung (Art. 17 DSGVO)",
              "Einschränkung der Verarbeitung (Art. 18 DSGVO)",
              "Datenübertragbarkeit (Art. 20 DSGVO)",
              "Widerruf erteilter Einwilligungen mit Wirkung für die Zukunft (Art. 7 Abs. 3 DSGVO)",
              "Beschwerde bei einer Datenschutz-Aufsichtsbehörde (Art. 77 DSGVO), insbesondere in dem Mitgliedstaat Ihres Aufenthaltsorts, Ihres Arbeitsplatzes oder des Orts des mutmaßlichen Verstoßes"]),
          p("Zur Ausübung Ihrer Rechte genügt eine formlose Nachricht an <a href=\"mailto:info@medluxlife.com\">info@medluxlife.com</a>.")]
    b += [h("13. Widerspruchsrecht (Art. 21 DSGVO)"),
          p("<strong>Soweit wir Ihre Daten auf Grundlage berechtigter Interessen (Art. 6 Abs. 1 lit. f DSGVO) verarbeiten, haben Sie das Recht, aus Gründen, die sich aus Ihrer besonderen Situation ergeben, jederzeit Widerspruch gegen diese Verarbeitung einzulegen. Wir verarbeiten die Daten dann nicht mehr, es sei denn, wir können zwingende schutzwürdige Gründe nachweisen, die Ihre Interessen, Rechte und Freiheiten überwiegen, oder die Verarbeitung dient der Geltendmachung, Ausübung oder Verteidigung von Rechtsansprüchen.</strong>")]
    b += [h("14. Pflicht zur Bereitstellung, automatisierte Entscheidungen"),
          p("Die Bereitstellung Ihrer Daten ist weder gesetzlich noch vertraglich vorgeschrieben. Ohne die als Pflichtfelder gekennzeichneten Angaben können wir Ihre Anfrage jedoch nicht bearbeiten. Eine automatisierte Entscheidungsfindung einschließlich Profiling (Art. 22 DSGVO) findet nicht statt.")]
    b += [h("15. Änderungen dieser Datenschutzerklärung"),
          p("Wir passen diese Datenschutzerklärung an, sobald Änderungen der Website, unserer Leistungen oder der Rechtslage dies erforderlich machen. Es gilt die jeweils auf dieser Seite veröffentlichte Fassung.")]
    return group(b, "medlux-legal")

def terms():
    b = [note(), p(f"Stand: {DATE}")]
    b += [h("§ 1 Geltungsbereich und Anbieter"),
          p(f"(1) Diese Allgemeinen Geschäftsbedingungen (AGB) gelten für alle Verträge zwischen MedLuxLife, {COMPANY}, {ADDRESS} (nachfolgend „MedLuxLife“ oder „wir“), und ihren Kundinnen und Kunden (nachfolgend „Kunde“) über die auf der Website {B.split('//')[1]} angebotenen Leistungen."),
          p("(2) Verbraucher im Sinne dieser AGB ist jede natürliche Person, die ein Rechtsgeschäft zu Zwecken abschließt, die überwiegend weder ihrer gewerblichen noch ihrer selbständigen beruflichen Tätigkeit zugerechnet werden können (§ 13 BGB)."),
          p("(3) Abweichende Bedingungen des Kunden werden nicht anerkannt, es sei denn, wir stimmen ihrer Geltung ausdrücklich in Textform zu. Individuelle Vereinbarungen im jeweiligen Angebot haben Vorrang vor diesen AGB.")]
    b += [h("§ 2 Leistungen von MedLuxLife"),
          p("(1) <strong>Gesundheitsleistungen (Health):</strong> MedLuxLife informiert über medizinische Behandlungsmöglichkeiten, stellt den Kontakt zu Partnerkliniken und Fachärzten her und unterstützt bei der Organisation (z. B. Terminabstimmung, Kommunikation, Unterkunft, Transfers, Betreuung vor Ort und nach der Rückkehr)."),
          p("(2) <strong>MedLuxLife erbringt selbst keine ärztlichen oder sonstigen Heilbehandlungen</strong> und gibt keine medizinischen Empfehlungen oder Diagnosen. Über die Eignung, Art und Durchführung einer Behandlung entscheiden ausschließlich die behandelnden Ärztinnen und Ärzte nach ärztlicher Aufklärung. Der Behandlungsvertrag kommt unmittelbar zwischen dem Kunden und der jeweiligen Klinik bzw. dem behandelnden Arzt zustande; für diesen gelten deren Bedingungen."),
          p("(3) Ein bestimmter Behandlungserfolg ist nicht Gegenstand unserer Leistungen und kann von uns nicht zugesagt werden. Informationen auf der Website dienen der allgemeinen Orientierung und ersetzen keine ärztliche Beratung."),
          p("(4) <strong>Reiseleistungen (Travel):</strong> MedLuxLife vermittelt Reiseleistungen Dritter, insbesondere Hotelunterkünfte, Flugtickets, Flughafentransfers, Urlaubspakete sowie Hajj- und Umrah-Reisen. Wir handeln dabei als Vermittler; der Vertrag über die jeweilige Reiseleistung kommt zwischen dem Kunden und dem jeweiligen Leistungsträger bzw. Reiseveranstalter zustande, dessen Geschäfts- und Beförderungsbedingungen ergänzend gelten. Unsere Pflichten als Reisevermittler nach §§ 651v ff. BGB bleiben unberührt."),
          p("(5) MedLuxLife ist <strong>kein Reiseveranstalter</strong>. Urlaubspakete sowie Hajj- und Umrah-Reisen werden von dem jeweils im Angebot genannten Reiseveranstalter durchgeführt. Dieser ist Vertragspartner des Kunden, für die Erbringung der Reiseleistungen sowie für die gesetzlich vorgeschriebene Insolvenzabsicherung verantwortlich und stellt dem Kunden das gesetzlich vorgeschriebene Formblatt sowie den Sicherungsschein zur Verfügung. MedLuxLife leitet diese Unterlagen vor der Buchung an den Kunden weiter."),
          p("(6) Die Gesundheits- und die Reiseleistungen sind voneinander unabhängig und können getrennt in Anspruch genommen werden.")]
    b += [h("§ 3 Vertragsschluss"),
          p("(1) Die Darstellung der Leistungen auf der Website stellt kein verbindliches Angebot dar, sondern eine Aufforderung zur Anfrage."),
          p("(2) Nach Ihrer Anfrage (über das Kontaktformular, per E-Mail, Telefon oder WhatsApp) erstellen wir Ihnen ein individuelles Angebot in Textform. Der Vertrag kommt zustande, wenn Sie dieses Angebot in Textform annehmen oder wir Ihre Buchung in Textform bestätigen."),
          p("(3) Die Vertragssprache ist Deutsch. Auf Wunsch kann die Kommunikation auch auf Englisch, Türkisch, Ukrainisch oder Russisch erfolgen; maßgeblich bleibt die deutsche Fassung.")]
    b += [h("§ 4 Preise und Zahlung"),
          p("(1) Die Erstberatung ist kostenlos und unverbindlich."),
          p("(2) Preise, Leistungsumfang, Fälligkeit und Zahlungsweise ergeben sich aus dem individuellen Angebot. Für vermittelte Leistungen Dritter (z. B. Behandlungskosten, Hotel, Flug) gelten die Preise und Zahlungsbedingungen des jeweiligen Leistungsträgers, sofern im Angebot nichts anderes vereinbart ist."),
          p("(3) Die Kosten einer medizinischen Behandlung im Ausland werden in der Regel nicht oder nur teilweise von gesetzlichen oder privaten Krankenversicherungen übernommen. Die Klärung einer Kostenübernahme obliegt dem Kunden.")]
    b += [h("§ 5 Mitwirkungspflichten des Kunden"),
          p("Der Kunde ist verpflichtet,"),
          ul(["vollständige und wahrheitsgemäße Angaben zu machen, insbesondere gegenüber den behandelnden Ärzten zu Gesundheitszustand, Vorerkrankungen und Medikamenten,",
              "für gültige Reisedokumente (Reisepass, Visum) sowie die Einhaltung von Einreise-, Gesundheits- und Impfbestimmungen selbst zu sorgen; dies gilt insbesondere für die besonderen Einreise- und Impfvorschriften bei Hajj- und Umrah-Reisen,",
              "Änderungen seiner Kontaktdaten oder Reisedaten unverzüglich mitzuteilen,",
              "den Abschluss geeigneter Versicherungen (z. B. Auslandskranken-, Reiserücktritts- oder Komplikationsversicherung) eigenverantwortlich zu prüfen."])]
    b += [h("§ 6 Änderungen und Stornierung"),
          p("(1) Wünscht der Kunde Änderungen oder storniert er eine Leistung, richten sich die Folgen nach dem individuellen Angebot sowie nach den Bedingungen des jeweiligen Leistungsträgers (z. B. Stornobedingungen des Hotels, der Fluggesellschaft oder der Klinik)."),
          p("(2) Medizinisch bedingte Terminänderungen, die die behandelnden Ärzte veranlassen, liegen nicht im Einflussbereich von MedLuxLife. Wir unterstützen den Kunden in diesem Fall bei der Umorganisation.")]
    b += [h("§ 7 Widerrufsrecht"),
          p("(1) Verbrauchern steht bei Verträgen, die ausschließlich über Fernkommunikationsmittel geschlossen werden, grundsätzlich ein gesetzliches Widerrufsrecht zu. Die Einzelheiten ergeben sich aus der Widerrufsbelehrung, die wir dem Kunden zusammen mit dem Angebot zur Verfügung stellen."),
          p("(2) Das Widerrufsrecht besteht nach § 312g Abs. 2 Nr. 9 BGB nicht bei Verträgen über die Erbringung von Dienstleistungen in den Bereichen Beherbergung (außer zu Wohnzwecken), Beförderung, Lieferung von Speisen und Getränken sowie Freizeitbetätigungen, wenn der Vertrag für die Erbringung einen spezifischen Termin oder Zeitraum vorsieht. Bei Pauschalreiseverträgen besteht das gesetzliche Rücktrittsrecht nach § 651h BGB.")]
    b += [h("§ 8 Haftung"),
          p("(1) MedLuxLife haftet unbeschränkt für Vorsatz und grobe Fahrlässigkeit, für Schäden aus der Verletzung des Lebens, des Körpers oder der Gesundheit, die auf einer Pflichtverletzung von MedLuxLife beruhen, sowie nach dem Produkthaftungsgesetz."),
          p("(2) Bei leicht fahrlässiger Verletzung einer wesentlichen Vertragspflicht (Kardinalpflicht), deren Erfüllung die ordnungsgemäße Durchführung des Vertrags überhaupt erst ermöglicht und auf deren Einhaltung der Kunde regelmäßig vertrauen darf, ist die Haftung auf den vertragstypischen, vorhersehbaren Schaden begrenzt. Im Übrigen ist die Haftung für leichte Fahrlässigkeit ausgeschlossen."),
          p("(3) Für die Erbringung der vermittelten Leistungen selbst – insbesondere für ärztliche Behandlungen und deren Ergebnis sowie für Leistungen von Hotels, Fluggesellschaften, Transferunternehmen und Reiseveranstaltern – haften ausschließlich die jeweiligen Leistungserbringer. Die Haftung von MedLuxLife für eigene Pflichtverletzungen, insbesondere bei der Vermittlung, bleibt hiervon unberührt."),
          p("(4) Die vorstehenden Haftungsbeschränkungen gelten auch zugunsten unserer Mitarbeiter und Erfüllungsgehilfen.")]
    b += [h("§ 9 Datenschutz"),
          p(f"Informationen zur Verarbeitung Ihrer personenbezogenen Daten finden Sie in unserer <a href=\"{B}/privacy-policy/\">Datenschutzerklärung</a>.")]
    b += [h("§ 10 Verbraucherstreitbeilegung"),
          p("Wir sind nicht bereit und nicht verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.")]
    b += [h("§ 11 Schlussbestimmungen"),
          p("(1) Es gilt das Recht der Bundesrepublik Deutschland unter Ausschluss des UN-Kaufrechts. Gegenüber Verbrauchern gilt diese Rechtswahl nur insoweit, als nicht der gewährte Schutz durch zwingende Bestimmungen des Rechts des Staates, in dem der Verbraucher seinen gewöhnlichen Aufenthalt hat, entzogen wird."),
          p("(2) Ist der Kunde Kaufmann, juristische Person des öffentlichen Rechts oder öffentlich-rechtliches Sondervermögen, ist ausschließlicher Gerichtsstand für alle Streitigkeiten aus diesem Vertrag unser Geschäftssitz."),
          p("(3) Sollten einzelne Bestimmungen dieser AGB unwirksam sein oder werden, bleibt die Wirksamkeit der übrigen Bestimmungen unberührt. An die Stelle der unwirksamen Bestimmung treten die gesetzlichen Vorschriften.")]
    return group(b, "medlux-legal")

if __name__ == "__main__":
    out = sys.argv[1]
    json.dump({"privacy": {"title": "Datenschutzerklärung", "slug": "privacy-policy", "status": "publish", "template": "page-with-title-general", "content": privacy()},
               "terms": {"title": "AGB", "slug": "terms", "status": "publish", "template": "page-with-title-general", "content": terms()}},
              open(out, "w"), ensure_ascii=False)
