"""Travel hub page (25) with five sections, and the five travel sub-pages."""
import json, os
from blocks import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = {k: tuple(v) for k, v in json.load(open(os.path.join(HERE, 'images.json'))).items()}
T = B + "/travel/"

SERVICES = [  # (page id, title, slug, image key, summary, highlights)
    (275, "Holiday Packages", "holiday-packages", "travel-holiday-packages",
     "Relax before or after your treatment, or simply enjoy a holiday: tailor-made stays at the coast, in historic cities or in quiet resorts.",
     ["Tailor-made itineraries", "Seaside, city and wellness stays", "Recovery-friendly planning after treatment"]),
    (276, "Hotel Reservation", "hotel-reservation", "travel-hotel-reservation",
     "Carefully selected hotels close to your clinic or in the area you prefer, from comfortable city hotels to five-star resorts.",
     ["Hotels near your clinic or hospital", "Rooms for companions and families", "Flexible dates around your treatment"]),
    (283, "Flight Tickets", "flight-tickets", "travel-flight-tickets",
     "We find suitable flights from your home airport and coordinate the dates with your appointments and hotel stay.",
     ["Flights from your home airport", "Dates matched to your appointments", "Help with changes and rebooking"]),
    (277, "Airport Transfer", "airport-transfer", "travel-airport-transfer",
     "A private driver meets you at the airport and takes you to your hotel, and we arrange transfers between hotel, clinic and airport.",
     ["Private meet-and-greet at arrival", "Transfers to clinic and hospital", "Comfortable vehicles for you and your companions"]),
    (278, "Hajj &amp; Umrah", "hajj-umrah", "travel-hajj-umrah",
     "Calm, well-organised Umrah and Hajj journeys with licensed partners, including visa guidance, flights, hotels near the holy sites and transfers.",
     ["Umrah journeys throughout the year", "Hajj with licensed partners, subject to quotas", "Hotels near the holy mosques"]),
]

def travel_process():
    steps = [
        ("1. Tell us your plans", "Share your dates, destination and wishes, and who will travel with you."),
        ("2. Personal offer", "We prepare a tailored proposal for flights, hotel and transfers, without obligation."),
        ("3. Booking and documents", "Once you agree, we make the bookings and send you all travel documents."),
        ("4. Support during your trip", "We are available for you before and during your journey."),
    ]
    return group([h("How it works")] + [grid([card(t, [p(d)]) for t, d in steps], "medlux-steps")], "medlux-section")

def travel_cta(topic):
    return group([
        h(f"Plan your {topic} with us"),
        p("Tell us what you have in mind and we will prepare a personal, no-obligation offer for you."),
        buttons([
            ("Request an Offer", B + "/contact/", "medlux-btn-primary", ""),
            ("WhatsApp", WHATSAPP, "medlux-btn-whatsapp", ' target="_blank" rel="noreferrer noopener"'),
        ]),
    ], "medlux-cta")

def section_row(i, pid, title, slug, img_key, summary, highlights):
    text = [h(title), p(summary), ul(highlights), buttons([(f"Discover {title}", T + slug + "/", "medlux-btn-primary", "")])]
    cols = [('<!-- wp:column {"className":"medlux-row-media"} -->\n<div class="wp-block-column medlux-row-media">'
             + img(*IMG[img_key], cls="medlux-row-img") + '</div>\n<!-- /wp:column -->'),
            ('<!-- wp:column {"verticalAlignment":"center","className":"medlux-row-text"} -->\n<div class="wp-block-column is-vertically-aligned-center medlux-row-text">'
             + "\n\n".join(text) + '</div>\n<!-- /wp:column -->')]
    cls = "medlux-row" + (" medlux-row--reverse" if i % 2 else "")
    return (f'<!-- wp:columns {{"className":"{cls}"}} -->\n<div class="wp-block-columns {cls}">' + "\n\n".join(cols) + '</div>\n<!-- /wp:columns -->')

HUB = "\n\n".join([
    p("Whether you combine your treatment with a few days of rest or travel purely for pleasure or pilgrimage, MedLuxLife takes care of the details: holidays, hotels, flights, airport transfers and Hajj and Umrah journeys, all planned around you.", "medlux-lead"),
    group([h("Our travel services")] + [section_row(i, *s[:6]) for i, s in enumerate(SERVICES)], "medlux-section medlux-rows"),
    travel_process(),
    travel_cta("journey"),
])

def subpage(img_key, lead, cards, good_to_know, topic):
    parts = [intro(lead, IMG[img_key]),
             group([h("What we offer"), grid([card(t, [p(d)]) for t, d in cards])], "medlux-section")]
    if good_to_know:
        parts.append(group([h("Good to know"), ul(good_to_know)], "medlux-section"))
    return "\n\n".join(parts + [travel_process(), travel_cta(topic)])

PAGES = {25: HUB}

PAGES[275] = subpage("travel-holiday-packages",
    "A holiday can be the perfect complement to your treatment, or a journey in its own right. We put together tailor-made packages for the coast, historic cities and quiet resorts, planned around your wishes, your budget and, where relevant, your recovery.",
    [("Seaside holidays", "Relaxing stays at the coast, from boutique hotels to all-inclusive resorts."),
     ("City breaks", "Culture, history and cuisine in vibrant cities, with hotels in central locations."),
     ("Wellness and spa stays", "Calm resorts with spa facilities for rest and relaxation."),
     ("Recovery-friendly holidays", "Quiet accommodation and a relaxed pace after treatment, planned in line with your doctor's advice."),
     ("Holidays for companions", "Activities and excursions for family members who travel with you."),
     ("Excursions and tours", "Guided tours and day trips, booked for the dates that suit you.")],
    ["After surgery, some activities such as swimming, sunbathing or long flights may need to wait. We plan your holiday in line with your doctor's recommendations.",
     "Packages are put together individually; we send you a personal offer."],
    "holiday")

PAGES[276] = subpage("travel-hotel-reservation",
    "The right hotel makes your stay easier. We select and book accommodation that suits your needs, close to your clinic or hospital or in the area you prefer, and coordinate the dates with your appointments.",
    [("Hotels near your clinic", "Short distances to your appointments for a relaxed stay."),
     ("Comfort and five-star hotels", "From comfortable city hotels to luxury resorts."),
     ("Recovery-friendly rooms", "Quiet rooms and practical amenities for the days after treatment."),
     ("Companions and families", "Rooms and suites for those travelling with you."),
     ("Flexible dates", "Extensions or changes if your treatment plan changes."),
     ("Special requests", "Dietary needs, accessibility or other wishes passed on to the hotel.")],
    ["Hotel categories and room types are confirmed in your personal offer."],
    "hotel stay")

PAGES[283] = subpage("travel-flight-tickets",
    "We look for suitable flights from your home airport and coordinate the dates with your appointments and hotel, so that everything fits together.",
    [("Flights from your home airport", "Connections from Germany and other countries to your destination."),
     ("Dates matched to your treatment", "Arrival and departure planned around your appointments and recovery time."),
     ("Economy and business class", "The class of travel that suits you."),
     ("Companions", "Flights for family members or companions on the same itinerary."),
     ("Changes and rebooking", "Support if your dates need to change."),
     ("Fit to fly", "Departure dates planned in line with your doctor's advice after treatment.")],
    ["Fares and availability depend on the airline and the time of booking; you receive a personal offer before anything is booked.",
     "Please check that your passport and any required visas are valid for your journey."],
    "flights")

PAGES[277] = subpage("travel-airport-transfer",
    "Arrive relaxed: a private driver meets you at the airport and takes you to your hotel. During your stay we arrange transfers between your hotel, clinic or hospital and back to the airport.",
    [("Meet and greet", "Your driver welcomes you in the arrivals hall."),
     ("Airport to hotel", "A direct, private transfer to your accommodation."),
     ("Transfers to appointments", "Transport between hotel, clinic and hospital on treatment days."),
     ("Return to the airport", "A punctual transfer for your flight home."),
     ("Comfortable vehicles", "Clean, comfortable vehicles with space for luggage and companions."),
     ("Help on the way", "Contact with our team if you need anything during your stay.")],
    None,
    "transfers")

PAGES[278] = subpage("travel-hajj-umrah",
    "Hajj and Umrah are journeys of the heart. We help you prepare calmly and organise the practical details in cooperation with licensed partners, so that you can focus on your spiritual journey.",
    [("Umrah", "Umrah journeys throughout the year, for individuals, couples, families and groups."),
     ("Hajj", "Hajj journeys with licensed partners. Places are subject to quotas and registration rules set by the Saudi authorities."),
     ("Visa guidance", "Information on visa requirements and support with the application process."),
     ("Flights", "Flights to Jeddah or Medina, coordinated with your hotel and transfers."),
     ("Hotels near the holy mosques", "Accommodation in Mecca and Medina, close to the Haram where possible."),
     ("Transfers and guidance", "Transfers between airports, cities and hotels, and guidance during your journey.")],
    ["Hajj registration and quotas are regulated by the Saudi authorities and may differ by nationality and country of residence.",
     "Please make sure your passport is valid for at least six months and that required vaccinations, such as meningococcal vaccination, are up to date."],
    "Hajj or Umrah journey")
