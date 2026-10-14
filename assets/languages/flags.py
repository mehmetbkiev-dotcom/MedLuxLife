# Circular flag SVGs (viewBox 0 0 60 60, clipped to a circle) for the "We speak your language" band.
def wrap(inner, cid):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 60 60" width="60" height="60"><defs><clipPath id="{cid}"><circle cx="30" cy="30" r="30"/></clipPath></defs><g clip-path="url(#{cid})">{inner}</g></svg>'
F = {
 'de': ('Deutsch', wrap('<rect width="60" height="20" fill="#000"/><rect y="20" width="60" height="20" fill="#DD0000"/><rect y="40" width="60" height="20" fill="#FFCE00"/>', 'cde')),
 'en': ('English', wrap('<rect width="60" height="60" fill="#012169"/><path d="M0 0L60 60M60 0L0 60" stroke="#fff" stroke-width="12"/><path d="M0 0L60 60M60 0L0 60" stroke="#C8102E" stroke-width="5"/><path d="M30 0V60M0 30H60" stroke="#fff" stroke-width="18"/><path d="M30 0V60M0 30H60" stroke="#C8102E" stroke-width="10"/>', 'cen')),
 'tr': ('Türkçe', wrap('<rect width="60" height="60" fill="#E30A17"/><circle cx="25" cy="30" r="12" fill="#fff"/><circle cx="28" cy="30" r="9.6" fill="#E30A17"/><path fill="#fff" d="M35.5 30l9.2-3-5.7 7.8V25.2l5.7 7.8z"/>', 'ctr')),
 'ru': ('Русский', wrap('<rect width="60" height="20" fill="#fff"/><rect y="20" width="60" height="20" fill="#0039A6"/><rect y="40" width="60" height="20" fill="#D52B1E"/>', 'cru')),
 'uk': ('Українська', wrap('<rect width="60" height="30" fill="#0057B7"/><rect y="30" width="60" height="30" fill="#FFD700"/>', 'cuk')),
}
F.update({
 'fr': ('Français', wrap('<rect width="20" height="60" fill="#0055A4"/><rect x="20" width="20" height="60" fill="#fff"/><rect x="40" width="20" height="60" fill="#EF4135"/>', 'cfr')),
 'it': ('Italiano', wrap('<rect width="20" height="60" fill="#009246"/><rect x="20" width="20" height="60" fill="#fff"/><rect x="40" width="20" height="60" fill="#CE2B37"/>', 'cit')),
 'es': ('Español', wrap('<rect width="60" height="60" fill="#AA151B"/><rect y="15" width="60" height="30" fill="#F1BF00"/>', 'ces')),
 # Arabic: a language, not one country -> letter "ain" on green instead of a national flag
 'ar': ('العربية', wrap('<rect width="60" height="60" fill="#0B7A3E"/><text x="30" y="41" text-anchor="middle" font-family="Amiri, Noto Naskh Arabic, Arial, sans-serif" font-size="30" font-weight="700" fill="#fff">ع</text>', 'car')),
})
