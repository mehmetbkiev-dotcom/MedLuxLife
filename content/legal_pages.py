"""Datenschutzerklärung (page 3, /privacy-policy/) and AGB (/terms/) for MedLuxLife.

Written in German (binding version). Values in PH(...) are placeholders that must be
filled in before launch (legal entity, address, representative).
"""
import json, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from blocks import p, h, ul, group, B

def PH(t): return f'<mark class="medlux-placeholder">[{t}]</mark>'

COMPANY = "Inh. Anna Sacilanates (Einzelunternehmen)"
ADDRESS = "Stolberger Straße 21, 52068 Aachen, Deutschland"
CONTACT = f'Telefon: <a href="tel:+4916093448714">+49 160 93 44 87 14</a><br>E-Mail: <a href="mailto:info@medluxlife.com">info@medluxlife.com</a>'
DATE = "Oktober 2026"

def note():
    return p('<em>This document is provided in German, which is the legally binding version. Translations into other languages are provided for convenience only.</em>', "medlux-legal-note")

def privacy():
    # Final text supplied by the owner on 2026-10-06 (source notes/links left out).
    MAIL = '<a href="mailto:info@medluxlife.com">info@medluxlife.com</a>'
    b = [note(), p(f"Stand: {DATE}")]
    b += [h("1. Verantwortlicher"),
          p("Verantwortlich für die Verarbeitung personenbezogener Daten auf dieser Website im Sinne der Datenschutz-Grundverordnung (DSGVO) ist:"),
          p(f"MedLuxLife<br>{COMPANY}<br>Stolberger Straße 21<br>52068 Aachen, Deutschland<br>{CONTACT}"),
          p("Bei Fragen zum Datenschutz können Sie sich jederzeit unter den oben genannten Kontaktdaten an uns wenden.")]
    b += [h("2. Überblick"),
          p("Wir verarbeiten personenbezogene Daten nur, soweit dies zur Bereitstellung einer funktionsfähigen Website, zur Bearbeitung und Beantwortung Ihrer Anfragen sowie zur Erbringung unserer Leistungen erforderlich ist."),
          p("Auf dieser Website setzen wir derzeit keine Analyse-, Tracking- oder Marketing-Tools ein und binden keine Social-Media-Plugins ein."),
          p("Rechtsgrundlagen der Verarbeitung sind insbesondere:"),
          ul(["Art. 6 Abs. 1 lit. a DSGVO – Einwilligung,",
              "Art. 6 Abs. 1 lit. b DSGVO – Vertragserfüllung und vorvertragliche Maßnahmen,",
              "Art. 6 Abs. 1 lit. c DSGVO – Erfüllung rechtlicher Verpflichtungen,",
              "Art. 6 Abs. 1 lit. f DSGVO – berechtigte Interessen,",
              "Art. 9 Abs. 2 lit. a DSGVO – ausdrückliche Einwilligung bei Gesundheitsdaten."])]
    b += [h("3. Hosting und Server-Logfiles"),
          p("Diese Website wird bei der IONOS SE, Elgendorfer Straße 57, 56410 Montabaur, Deutschland, gehostet. Mit IONOS besteht ein Vertrag zur Auftragsverarbeitung gemäß Art. 28 DSGVO."),
          p("Beim Aufruf unserer Website werden durch den Server automatisch Informationen erfasst, die Ihr Browser übermittelt. Hierzu können insbesondere gehören:"),
          ul(["IP-Adresse,", "Datum und Uhrzeit des Zugriffs,", "aufgerufene Seite bzw. Datei,", "Referrer-URL,", "Browsertyp und Browserversion,", "verwendetes Betriebssystem."]),
          p("Die Verarbeitung erfolgt auf Grundlage von Art. 6 Abs. 1 lit. f DSGVO. Unser berechtigtes Interesse liegt insbesondere in der sicheren, zuverlässigen und stabilen Bereitstellung unserer Website sowie in der Erkennung und Abwehr von Angriffen und Missbrauch."),
          p("Server-Logfiles werden nur so lange gespeichert, wie dies für diese Zwecke erforderlich ist bzw. entsprechend den geltenden Vorgaben und Einstellungen des Hosting-Anbieters.")]
    b += [h("4. SSL-/TLS-Verschlüsselung"),
          p("Diese Website nutzt aus Sicherheitsgründen und zum Schutz der Übertragung vertraulicher Inhalte eine SSL- bzw. TLS-Verschlüsselung. Eine verschlüsselte Verbindung erkennen Sie insbesondere daran, dass die Adresszeile Ihres Browsers mit „https://“ beginnt.")]
    b += [h("5. Cookies und Spracheinstellungen"),
          p("Wir verwenden ausschließlich technisch notwendige Cookies bzw. vergleichbare Technologien, soweit diese für den Betrieb unserer Website oder die Bereitstellung einer vom Nutzer ausdrücklich gewünschten Funktion erforderlich sind. Hierzu kann beispielsweise die Speicherung der vom Nutzer ausgewählten Sprache gehören."),
          p("Soweit diese Technologien unbedingt erforderlich sind, erfolgt ihre Verwendung auf Grundlage von § 25 Abs. 2 Nr. 2 TDDDG. Die damit verbundene Verarbeitung personenbezogener Daten erfolgt, soweit einschlägig, auf Grundlage von Art. 6 Abs. 1 lit. f DSGVO."),
          p("Cookies zu Analyse-, Tracking- oder Werbezwecken setzen wir derzeit nicht ein."),
          p("Sie können Cookies über die Einstellungen Ihres Browsers löschen oder deren Speicherung einschränken. Bei der Deaktivierung technisch erforderlicher Funktionen kann die Nutzung einzelner Bereiche unserer Website eingeschränkt sein.")]
    b += [h("6. Kontaktformular"),
          p("Wenn Sie uns über das Kontaktformular eine Anfrage senden, verarbeiten wir die von Ihnen angegebenen Daten. Dies können insbesondere sein:"),
          ul(["Name,", "E-Mail-Adresse,", "Telefonnummer, soweit angegeben,", "gewünschter Bereich (Health oder Travel),", "Inhalt Ihrer Nachricht."]),
          p("Die Verarbeitung erfolgt zur Bearbeitung und Beantwortung Ihrer Anfrage."),
          p("Soweit Ihre Anfrage der Anbahnung oder Durchführung eines Vertrags dient, ist Rechtsgrundlage Art. 6 Abs. 1 lit. b DSGVO. Soweit die Verarbeitung auf einer von Ihnen erteilten Einwilligung beruht, ist Rechtsgrundlage Art. 6 Abs. 1 lit. a DSGVO. Eine erteilte Einwilligung kann jederzeit mit Wirkung für die Zukunft widerrufen werden."),
          p("Bitte übermitteln Sie über das allgemeine Kontaktformular keine ausführlichen medizinischen Informationen, Befunde, Röntgenbilder oder sonstigen Gesundheitsunterlagen. Soweit Gesundheitsdaten für die Bearbeitung Ihres Anliegens erforderlich werden, werden wir Sie gesondert darüber informieren und – soweit erforderlich – eine ausdrückliche Einwilligung einholen."),
          p("Für das Kontaktformular verwenden wir derzeit das WordPress-Plugin Contact Form 7. Nach unserer derzeitigen Konfiguration werden die über das Kontaktformular übermittelten Daten nicht dauerhaft in einer Datenbank der Website gespeichert, sondern zur Bearbeitung der Anfrage per E-Mail an uns übermittelt.")]
    b += [h("7. Kontakt per E-Mail, Telefon und WhatsApp"),
          p("Wenn Sie uns per E-Mail oder Telefon kontaktieren, verarbeiten wir die von Ihnen übermittelten personenbezogenen Daten zur Bearbeitung Ihres Anliegens. Rechtsgrundlage ist insbesondere Art. 6 Abs. 1 lit. b DSGVO, soweit die Kommunikation der Anbahnung oder Durchführung eines Vertrags dient, und im Übrigen Art. 6 Abs. 1 lit. f DSGVO."),
          p("Auf unserer Website können wir außerdem einen Link zu WhatsApp bereitstellen. Es handelt sich hierbei um einen einfachen Link. Beim bloßen Besuch unserer Website werden über diesen Link grundsätzlich keine Daten an WhatsApp übertragen."),
          p("Erst wenn Sie den Link anklicken bzw. WhatsApp verwenden und uns dort kontaktieren, werden personenbezogene Daten wie beispielsweise Telefonnummer, Profilname, Nachrichteninhalte und technische Metadaten durch WhatsApp verarbeitet. Anbieter für Nutzer im Europäischen Wirtschaftsraum ist die WhatsApp Ireland Limited, Merrion Road, Dublin 4, D04 X2K5, Irland. Im Rahmen der Nutzung können Daten auch an Unternehmen der Meta-Unternehmensgruppe und gegebenenfalls in Drittländer übermittelt werden."),
          p("Die Nutzung von WhatsApp ist freiwillig. Sie können uns alternativ jederzeit per E-Mail oder Telefon kontaktieren."),
          p("Bitte senden Sie uns über WhatsApp keine Gesundheitsdaten, medizinischen Befunde, Röntgenbilder oder sonstigen medizinischen Unterlagen, sofern wir Sie nicht ausdrücklich darum gebeten und über die vorgesehene Verarbeitung informiert haben.")]
    b += [h("8. Verarbeitung im Rahmen unserer Leistungen"),
          h("Gesundheitsleistungen (Health)", 3),
          p("Wenn Sie unsere Unterstützung bei der Organisation bzw. Vermittlung einer medizinischen Behandlung in Anspruch nehmen, kann die Verarbeitung besonderer Kategorien personenbezogener Daten erforderlich sein. Hierzu können insbesondere gehören:"),
          ul(["Angaben zu Ihrem Gesundheitszustand,", "Vorerkrankungen,", "Befunde,", "Röntgenbilder,", "Fotografien,", "Behandlungsinformationen,", "sonstige medizinische Unterlagen."]),
          p("Soweit eine Verarbeitung solcher Gesundheitsdaten durch uns erforderlich ist, erfolgt diese grundsätzlich auf Grundlage Ihrer ausdrücklichen Einwilligung gemäß Art. 9 Abs. 2 lit. a DSGVO, die gesondert eingeholt wird."),
          p("Zur Einholung eines Behandlungsangebots, zur Erstellung eines Behandlungsplans, zur Terminorganisation und zur Durchführung der von Ihnen gewünschten Leistungen können die hierfür erforderlichen personenbezogenen Daten an die jeweilige Partnerklinik, behandelnde Ärztinnen und Ärzte oder andere erforderliche medizinische Leistungserbringer übermittelt werden."),
          h("Übermittlung von Gesundheitsdaten in die Türkei", 3),
          p("Unsere medizinischen Partner können sich insbesondere in der Türkei befinden. Bei einer Übermittlung personenbezogener Daten in die Türkei handelt es sich um eine Übermittlung in ein Drittland außerhalb der Europäischen Union bzw. des Europäischen Wirtschaftsraums."),
          p("Soweit für die betreffende Übermittlung kein Angemessenheitsbeschluss der Europäischen Kommission und keine anderen geeigneten Garantien im Sinne der Art. 45 und 46 DSGVO vorliegen, erfolgt eine Übermittlung insbesondere nur, wenn die gesetzlichen Voraussetzungen hierfür erfüllt sind. Bei einer auf Ihrer ausdrücklichen Einwilligung beruhenden Drittlandübermittlung erfolgt diese gemäß Art. 49 Abs. 1 lit. a DSGVO."),
          p("Vor Erteilung einer solchen Einwilligung werden Sie darüber informiert, dass bei einer Übermittlung in ein Drittland ohne Angemessenheitsbeschluss und ohne geeignete Garantien möglicherweise kein mit dem Datenschutzrecht der Europäischen Union vergleichbares Datenschutzniveau besteht. Hieraus können insbesondere Risiken hinsichtlich des Zugriffs auf Ihre Daten sowie der Durchsetzung Ihrer Datenschutzrechte entstehen."),
          p("Soweit eine Drittlandübermittlung zur Erfüllung eines Vertrags zwischen Ihnen und uns oder zur Durchführung auf Ihren Wunsch getroffener vorvertraglicher Maßnahmen erforderlich ist bzw. zur Erfüllung eines in Ihrem Interesse geschlossenen Vertrags erforderlich ist, können darüber hinaus die gesetzlichen Voraussetzungen des Art. 49 Abs. 1 lit. b bzw. lit. c DSGVO Anwendung finden."),
          p("Die jeweilige Partnerklinik bzw. die behandelnden Ärztinnen und Ärzte sind für die Verarbeitung personenbezogener Daten im Rahmen der eigentlichen medizinischen Behandlung grundsätzlich eigenständig verantwortlich, soweit keine andere datenschutzrechtliche Rollenverteilung besteht."),
          h("Reiseleistungen (Travel)", 3),
          p("Im Rahmen unserer Reiseleistungen können wir insbesondere bei der Vermittlung oder Organisation von"),
          ul(["Hotels,", "Flügen,", "Transfers,", "Reisepaketen,", "Hajj- und Umrah-Reisen"]),
          p("personenbezogene Daten verarbeiten. Je nach gebuchter oder angefragter Leistung können hierzu insbesondere gehören:"),
          ul(["Vor- und Nachname,", "Geburtsdatum,", "Kontaktdaten,", "Reisedaten,", "Pass- bzw. Ausweisdaten,", "sonstige für die jeweilige Buchung erforderliche Angaben."]),
          p("Soweit dies zur Durchführung der gewünschten Leistung erforderlich ist, übermitteln wir die notwendigen Daten an die jeweiligen Leistungsträger, beispielsweise Hotels, Fluggesellschaften, Transferunternehmen oder Reiseveranstalter. Rechtsgrundlage ist insbesondere Art. 6 Abs. 1 lit. b DSGVO."),
          p("Befindet sich ein Leistungsträger außerhalb der EU bzw. des EWR, beispielsweise in der Türkei oder in Saudi-Arabien, kann die Übermittlung personenbezogener Daten zur Erfüllung eines Vertrags bzw. zur Durchführung eines im Interesse der betroffenen Person geschlossenen Vertrags nach Maßgabe von Art. 49 Abs. 1 lit. b bzw. lit. c DSGVO erfolgen."),
          p("Bei Hajj- und Umrah-Reisen können personenbezogene Daten außerdem an die für Visa-, Einreise- oder sonstige behördliche Verfahren zuständigen Stellen bzw. hieran beteiligten Dienstleister übermittelt werden, soweit dies für die gewünschte Leistung erforderlich ist.")]
    b += [h("9. Empfänger personenbezogener Daten"),
          p("Innerhalb von MedLuxLife erhalten nur diejenigen Personen Zugriff auf personenbezogene Daten, die diese zur Bearbeitung des jeweiligen Anliegens benötigen. Je nach Art der angefragten oder gebuchten Leistung können externe Empfänger insbesondere sein:"),
          ul(["IONOS SE als Hosting- bzw. E-Mail-Dienstleister,", "Partnerkliniken,", "Ärztinnen und Ärzte bzw. medizinische Leistungserbringer,", "Hotels,", "Fluggesellschaften,", "Transferunternehmen,", "Reiseveranstalter,", "für Visa- und Einreiseverfahren erforderliche Stellen,", "Steuerberater und sonstige berufliche Berater,", "Behörden, soweit eine gesetzliche Verpflichtung zur Übermittlung besteht."]),
          p("Eine Weitergabe personenbezogener Daten an Dritte zu deren eigenen Werbezwecken findet nicht statt.")]
    b += [h("10. Links zu sozialen Netzwerken"),
          p("Auf unserer Website können sich einfache Links zu unseren Profilen in sozialen Netzwerken befinden, insbesondere zu Facebook, Instagram und X. Nach unserer derzeitigen Gestaltung handelt es sich um einfache Links und nicht um eingebettete Social-Media-Plugins. Beim bloßen Besuch unserer Website werden daher über diese Links grundsätzlich keine personenbezogenen Daten an die jeweiligen sozialen Netzwerke übertragen."),
          p("Erst wenn Sie einen entsprechenden Link anklicken, verlassen Sie unsere Website und rufen die Website bzw. App des jeweiligen Anbieters auf. Für die dort stattfindende Datenverarbeitung gelten die Datenschutzbestimmungen des jeweiligen Anbieters.")]
    b += [h("11. Speicherdauer"),
          p("Wir speichern personenbezogene Daten grundsätzlich nur so lange, wie dies für den jeweiligen Verarbeitungszweck erforderlich ist."),
          p("Anfragen, aus denen kein Vertragsverhältnis entsteht, löschen wir grundsätzlich spätestens sechs Monate nach Abschluss der Kommunikation, sofern keine gesetzlichen Aufbewahrungspflichten, berechtigten Interessen oder sonstigen Rechtsgründe einer Löschung entgegenstehen."),
          p("Daten im Zusammenhang mit Verträgen speichern wir grundsätzlich für die Dauer der Vertragsbeziehung und anschließend nur insoweit weiter, wie dies aufgrund gesetzlicher Aufbewahrungspflichten oder zur Geltendmachung, Ausübung oder Verteidigung von Rechtsansprüchen erforderlich ist. Je nach Art der Unterlagen können insbesondere handels- und steuerrechtliche Aufbewahrungsfristen von sechs, acht oder zehn Jahren gelten."),
          p("Gesundheitsdaten, die wir ausschließlich zur Organisation oder Vermittlung einer Behandlung verarbeiten, löschen wir grundsätzlich, sobald sie für diesen Zweck nicht mehr erforderlich sind bzw. wenn eine zugrunde liegende Einwilligung wirksam widerrufen wurde, sofern keine gesetzlichen Aufbewahrungspflichten oder andere Rechtsgrundlagen einer Löschung entgegenstehen.")]
    b += [h("12. Ihre Rechte"),
          p("Sie haben nach Maßgabe der gesetzlichen Voraussetzungen insbesondere folgende Rechte:"),
          ul(["Recht auf Auskunft gemäß Art. 15 DSGVO,", "Recht auf Berichtigung gemäß Art. 16 DSGVO,", "Recht auf Löschung gemäß Art. 17 DSGVO,", "Recht auf Einschränkung der Verarbeitung gemäß Art. 18 DSGVO,", "Recht auf Datenübertragbarkeit gemäß Art. 20 DSGVO,", "Recht auf Widerspruch gemäß Art. 21 DSGVO,", "Recht auf Widerruf einer erteilten Einwilligung gemäß Art. 7 Abs. 3 DSGVO,", "Recht auf Beschwerde bei einer Datenschutzaufsichtsbehörde gemäß Art. 77 DSGVO."]),
          p("Der Widerruf einer Einwilligung berührt nicht die Rechtmäßigkeit der aufgrund der Einwilligung bis zum Widerruf erfolgten Verarbeitung."),
          p("Zur Ausübung Ihrer Rechte können Sie sich jederzeit an uns wenden:"),
          p(f"MedLuxLife<br>Inh. Anna Sacilanates<br>E-Mail: {MAIL}"),
          h("Zuständige Datenschutzaufsichtsbehörde", 3),
          p("Sie haben außerdem das Recht, sich bei einer Datenschutzaufsichtsbehörde zu beschweren. Für unseren Unternehmenssitz in Nordrhein-Westfalen ist insbesondere zuständig:"),
          p('Landesbeauftragte für Datenschutz und Informationsfreiheit Nordrhein-Westfalen (LDI NRW)<br>Kavalleriestraße 2–4<br>40213 Düsseldorf<br>Telefon: +49 211 38424-0<br>E-Mail: <a href="mailto:poststelle@ldi.nrw.de">poststelle@ldi.nrw.de</a><br>Website: <a href="https://www.ldi.nrw.de/" target="_blank" rel="noopener">www.ldi.nrw.de</a>')]
    b += [h("13. Widerspruchsrecht nach Art. 21 DSGVO"),
          p("<strong>Soweit wir Ihre personenbezogenen Daten auf Grundlage berechtigter Interessen gemäß Art. 6 Abs. 1 lit. f DSGVO verarbeiten, haben Sie das Recht, aus Gründen, die sich aus Ihrer besonderen Situation ergeben, jederzeit Widerspruch gegen diese Verarbeitung einzulegen.</strong>"),
          p("<strong>Wir verarbeiten die betreffenden personenbezogenen Daten anschließend nicht mehr, es sei denn, wir können zwingende schutzwürdige Gründe für die Verarbeitung nachweisen, die Ihre Interessen, Rechte und Freiheiten überwiegen, oder die Verarbeitung dient der Geltendmachung, Ausübung oder Verteidigung von Rechtsansprüchen.</strong>")]
    b += [h("14. Pflicht zur Bereitstellung von Daten und automatisierte Entscheidungen"),
          p("Die Bereitstellung personenbezogener Daten ist grundsätzlich weder gesetzlich noch vertraglich vorgeschrieben, soweit wir Sie im Einzelfall nicht ausdrücklich auf etwas anderes hinweisen. Ohne die für eine konkrete Anfrage, Buchung oder Leistung erforderlichen Angaben können wir das jeweilige Anliegen jedoch möglicherweise nicht bearbeiten bzw. die gewünschte Leistung nicht erbringen."),
          p("Eine automatisierte Entscheidungsfindung einschließlich Profiling im Sinne des Art. 22 DSGVO findet nicht statt.")]
    b += [h("15. Datensicherheit"),
          p("Wir treffen angemessene technische und organisatorische Maßnahmen, um personenbezogene Daten vor Verlust, Manipulation, unbefugtem Zugriff und sonstiger unzulässiger Verarbeitung zu schützen. Unsere Sicherheitsmaßnahmen werden entsprechend der technischen Entwicklung und unter Berücksichtigung der Art, des Umfangs und der Zwecke der Verarbeitung angemessen überprüft und angepasst.")]
    b += [h("16. Änderungen dieser Datenschutzerklärung"),
          p("Wir behalten uns vor, diese Datenschutzerklärung anzupassen, wenn Änderungen unserer Website, unserer Dienstleistungen, der eingesetzten technischen Systeme oder der Rechtslage dies erforderlich machen. Es gilt die jeweils auf dieser Website veröffentlichte aktuelle Fassung."),
          p(f"Stand: {DATE}")]
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

def impressum():
    b = [h("Angaben gemäß § 5 DDG"),
         p(f"MedLuxLife<br>{COMPANY}<br>{ADDRESS}"),
         h("Kontakt"),
         p(CONTACT),
         h("Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV"),
         p(f"Anna Sacilanates<br>{ADDRESS}"),
         h("Verbraucherstreitbeilegung"),
         p("Wir sind nicht bereit und nicht verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen."),
         h("Hinweis zu medizinischen Inhalten"),
         p("MedLuxLife erbringt keine ärztlichen Leistungen. Die Informationen auf dieser Website dienen ausschließlich der allgemeinen Information und ersetzen keine ärztliche Beratung, Diagnose oder Behandlung. Über die Eignung einer Behandlung entscheiden allein die behandelnden Ärztinnen und Ärzte."),
         h("Haftung für Inhalte"),
         p("Die Inhalte dieser Website wurden mit größtmöglicher Sorgfalt erstellt. Für die Richtigkeit, Vollständigkeit und Aktualität der Inhalte können wir jedoch keine Gewähr übernehmen. Als Diensteanbieter sind wir für eigene Inhalte auf diesen Seiten nach den allgemeinen Gesetzen verantwortlich. Verpflichtungen zur Entfernung oder Sperrung der Nutzung von Informationen nach den allgemeinen Gesetzen bleiben unberührt."),
         h("Haftung für Links"),
         p("Unsere Website enthält Links zu externen Websites Dritter, auf deren Inhalte wir keinen Einfluss haben. Für die Inhalte der verlinkten Seiten ist stets der jeweilige Anbieter oder Betreiber verantwortlich. Bei Bekanntwerden von Rechtsverletzungen werden wir derartige Links umgehend entfernen."),
         h("Urheberrecht"),
         p("Die auf dieser Website veröffentlichten Inhalte und Werke unterliegen dem deutschen Urheberrecht. Die Vervielfältigung, Bearbeitung, Verbreitung und jede Art der Verwertung außerhalb der Grenzen des Urheberrechts bedürfen der vorherigen schriftlichen Zustimmung von MedLuxLife.")]
    return group(b, "medlux-legal")

def health_consent():
    # Text supplied by the owner on 2026-10-06.
    b = [note(), p(f"Stand: {DATE}")]
    b += [h("Datenschutzrechtliche Einwilligung"),
          p(f"Im Rahmen meiner Anfrage bei MedLuxLife, {COMPANY}, {ADDRESS}, kann es erforderlich sein, personenbezogene Daten und insbesondere Gesundheitsdaten zu verarbeiten und an die für meine Anfrage ausgewählten medizinischen Leistungserbringer zu übermitteln."),
          p("Hierzu können insbesondere folgende Daten gehören:"),
          ul(["Vor- und Nachname sowie Kontaktdaten", "Angaben zur gewünschten Behandlung", "Angaben zum Gesundheitszustand und zu Vorerkrankungen", "medizinische Befunde und Arztberichte", "Röntgenbilder und sonstige medizinische Aufnahmen", "Fotos, soweit diese für die Beurteilung der gewünschten Behandlung erforderlich sind", "sonstige von mir zur medizinischen Beurteilung bereitgestellte Informationen und Unterlagen"])]
    b += [h("Zweck der Verarbeitung"),
          p("Die Verarbeitung und Übermittlung erfolgt ausschließlich, soweit dies zur Bearbeitung meiner Anfrage erforderlich ist, insbesondere zur:"),
          ul(["medizinischen Vorprüfung meiner Anfrage,", "Einholung einer medizinischen Einschätzung,", "Erstellung eines Behandlungs- bzw. Kostenvorschlags,", "Auswahl und Abstimmung mit einer geeigneten Partnerklinik bzw. behandelnden Ärztinnen und Ärzten,", "Organisation und Koordination von Behandlungsterminen,", "Vorbereitung der von mir gewünschten medizinischen Behandlung."])]
    b += [h("Ausdrückliche Einwilligung in die Verarbeitung von Gesundheitsdaten"),
          p("Gesundheitsdaten gehören zu den besonderen Kategorien personenbezogener Daten im Sinne von Art. 9 DSGVO."),
          p("Ich willige ausdrücklich gemäß Art. 9 Abs. 2 lit. a DSGVO ein, dass MedLuxLife die von mir bereitgestellten Gesundheitsdaten für die oben genannten Zwecke verarbeitet.")]
    b += [h("Übermittlung in die Türkei"),
          p("Mir ist bekannt, dass die für meine Anfrage ausgewählte Partnerklinik, behandelnde Ärztin bzw. der behandelnde Arzt oder ein anderer medizinischer Leistungserbringer seinen Sitz in der Türkei haben kann."),
          p("Soweit dies für die Bearbeitung meiner Anfrage und die Vorbereitung der von mir gewünschten Behandlung erforderlich ist, willige ich ausdrücklich ein, dass MedLuxLife die hierfür erforderlichen personenbezogenen Daten einschließlich meiner Gesundheitsdaten an den jeweiligen medizinischen Leistungserbringer in der Türkei übermittelt."),
          p("Ich willige ausdrücklich gemäß Art. 49 Abs. 1 lit. a DSGVO in diese Drittlandübermittlung ein.")]
    b += [h("Hinweis auf mögliche Risiken der Drittlandübermittlung"),
          p("Ich wurde darüber informiert, dass die Türkei ein Drittland außerhalb der Europäischen Union und des Europäischen Wirtschaftsraums ist und für die Türkei derzeit kein Angemessenheitsbeschluss der Europäischen Kommission besteht."),
          p("Mir ist insbesondere bekannt, dass bei einer Übermittlung in ein Drittland ohne Angemessenheitsbeschluss und ohne geeignete Garantien möglicherweise kein mit dem Datenschutzrecht der Europäischen Union vergleichbares Datenschutzniveau gewährleistet ist. Dies kann insbesondere bedeuten, dass:"),
          ul(["meine personenbezogenen Daten einem anderen gesetzlichen Datenschutzniveau unterliegen,", "staatliche Stellen unter den dort geltenden gesetzlichen Voraussetzungen Zugriff auf Daten erhalten können,", "meine datenschutzrechtlichen Betroffenenrechte möglicherweise schwieriger durchsetzbar sind,", "mir gegebenenfalls nicht dieselben Rechtsbehelfe und Durchsetzungsmöglichkeiten wie innerhalb der EU bzw. des EWR zur Verfügung stehen."])]
    b += [h("Freiwilligkeit und Widerruf"),
          p("Die Erteilung dieser Einwilligung ist freiwillig."),
          p("Ohne meine Einwilligung kann MedLuxLife meine Gesundheitsdaten nicht auf dieser Grundlage verarbeiten bzw. an einen medizinischen Leistungserbringer in der Türkei übermitteln. Dadurch kann eine medizinische Beurteilung, Angebotserstellung oder Organisation der gewünschten Behandlung gegebenenfalls nicht möglich sein."),
          p("Ich kann meine Einwilligung jederzeit mit Wirkung für die Zukunft widerrufen. Der Widerruf berührt nicht die Rechtmäßigkeit der Verarbeitung, die aufgrund meiner Einwilligung bis zum Zeitpunkt des Widerrufs erfolgt ist."),
          p("Der Widerruf kann insbesondere per E-Mail gerichtet werden an:"),
          p('MedLuxLife<br>Inh. Anna Sacilanates<br>Stolberger Straße 21<br>52068 Aachen, Deutschland<br>E-Mail: <a href="mailto:info@medluxlife.com">info@medluxlife.com</a>'),
          p(f'Weitere Informationen zur Verarbeitung personenbezogener Daten und zu meinen Datenschutzrechten finde ich in der <a href="{B}/privacy-policy/">Datenschutzerklärung</a> von MedLuxLife.')]
    return group(b, "medlux-legal")

if __name__ == "__main__":
    out = sys.argv[1]
    json.dump({"privacy": {"title": "Datenschutzerklärung", "slug": "privacy-policy", "status": "publish", "template": "page-with-title-general", "content": privacy()},
               "terms": {"title": "AGB", "slug": "terms", "status": "publish", "template": "page-with-title-general", "content": terms()},
               "impressum": {"title": "Impressum", "slug": "impressum", "status": "publish", "template": "page-with-title-general", "content": impressum()},
               "consent": {"title": "Einwilligung Gesundheitsdaten", "slug": "einwilligung-gesundheitsdaten", "status": "publish", "template": "page-with-title-general", "content": health_consent()}},
              open(out, "w"), ensure_ascii=False)
