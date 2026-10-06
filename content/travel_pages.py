"""Travel hub page (25) with five sections, and the five travel sub-pages."""
import json, os
from blocks import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = {k: tuple(v) for k, v in json.load(open(os.path.join(HERE, 'images.json'))).items()}
T = B + "/travel/"

SERVICES = [  # (page id, title, slug, image key, summary, highlights)
    (275, "Holiday Packages", "holiday-packages", "travel-holiday-packages",
     "Tailor-made holidays at the coast, in historic cities or in quiet resorts, planned around your wishes and travel dates.",
     ["Tailor-made itineraries", "Seaside, city and wellness holidays", "Packages for couples, families and groups"]),
    (276, "Hotel Reservation", "hotel-reservation", "travel-hotel-reservation",
     "Carefully selected hotels in the city or region of your choice, from comfortable city hotels to five-star resorts.",
     ["City hotels, resorts and boutique hotels", "Rooms and suites for families and groups", "Special requests passed on to the hotel"]),
    (283, "Flight Tickets", "flight-tickets", "travel-flight-tickets",
     "Domestic and international flight tickets for holidays, business trips and family visits, with personal advice and support.",
     ["Domestic and international flights", "One-way, return and multi-city tickets", "Group bookings, changes and rebooking"]),
    (277, "Airport Transfer", "airport-transfer", "travel-airport-transfer",
     "A private driver meets you at the airport and takes you to your hotel, and we arrange transfers for excursions and back to the airport.",
     ["Private meet-and-greet at arrival", "Hotel, city and excursion transfers", "Comfortable vehicles for every group size"]),
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
    p("Whether you are planning a holiday, a city break, a business trip or a pilgrimage, MedLuxLife takes care of the details: holiday packages, hotels, flight tickets, airport transfers and Hajj and Umrah journeys, all planned around you.", "medlux-lead"),
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
    "We put together tailor-made holiday packages for the coast, historic cities and quiet resorts, combining flights, hotel, transfers and excursions in one plan that matches your wishes, your dates and your budget.",
    [("Seaside holidays", "Relaxing stays at the coast, from boutique hotels to all-inclusive resorts."),
     ("City breaks", "Culture, history and cuisine in vibrant cities, with hotels in central locations."),
     ("Wellness and spa holidays", "Calm resorts with spa facilities for rest and relaxation."),
     ("Family holidays", "Family-friendly hotels, activities for children and practical travel arrangements."),
     ("Group and special-occasion travel", "Trips for friends, associations, honeymoons and anniversaries."),
     ("Excursions and tours", "Guided tours and day trips, booked for the dates that suit you.")],
    ["Packages are put together individually; you receive a personal offer before anything is booked."],
    "holiday")

PAGES[276] = subpage("travel-hotel-reservation",
    "The right hotel makes all the difference. We select and book accommodation that suits your plans and preferences, in the city or region of your choice and for any length of stay.",
    [("City hotels", "Central locations for business trips, city breaks and shopping."),
     ("Resorts and five-star hotels", "Comfort and service for a relaxing holiday."),
     ("Boutique hotels", "Smaller, characterful hotels with a personal touch."),
     ("Families and groups", "Family rooms, suites and group reservations."),
     ("Short and long stays", "From one night to extended stays, with flexible dates where possible."),
     ("Special requests", "Dietary needs, accessibility or other wishes passed on to the hotel.")],
    ["Hotel categories, room types and conditions are confirmed in your personal offer."],
    "hotel stay")

PAGES[283] = subpage("travel-flight-tickets",
    "Whether for a holiday, a business trip or a visit to family and friends, we find and book suitable flights for you and stay by your side if plans change, just like a personal travel office.",
    [("International flights", "Flight tickets to destinations worldwide, with direct and connecting flights."),
     ("Domestic flights", "Domestic flights within Turkey and other countries."),
     ("One-way, return and multi-city", "The ticket type that fits your itinerary."),
     ("Economy, business and first class", "The class of travel that suits you and your budget."),
     ("Group and family bookings", "Tickets for families, groups, associations and companies."),
     ("Baggage and seat selection", "Extra baggage, seat reservations and special assistance requests."),
     ("Changes and cancellations", "Support with rebooking, date changes and cancellations according to the fare rules."),
     ("Personal advice", "Help with finding suitable connections and travel times.")],
    ["Fares and availability depend on the airline and the time of booking; you receive a personal offer before anything is booked.",
     "Please check that your passport and any required visas are valid for your journey."],
    "flights")

PAGES[277] = subpage("travel-airport-transfer",
    "Arrive relaxed: a private driver meets you at the airport and takes you directly to your hotel. We also arrange transfers for excursions, meetings and events, and back to the airport.",
    [("Meet and greet", "Your driver welcomes you in the arrivals hall."),
     ("Airport to hotel", "A direct, private transfer to your accommodation."),
     ("City and excursion transfers", "Transport for sightseeing, day trips, meetings and events."),
     ("Return to the airport", "A punctual transfer for your flight home."),
     ("Vehicles for every group", "From comfortable cars to minibuses for families and groups."),
     ("Help on the way", "Contact with our team if you need anything during your trip.")],
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
