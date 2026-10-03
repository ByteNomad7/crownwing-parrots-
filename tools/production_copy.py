"""Customer-facing launch copy without repeated development/stock disclaimers.

Keep availability by enquiry and factual care/policy information. The contact
form submits enquiries through Netlify Forms on the deployed website.
"""
import re


REPLACEMENTS = {
    "SPECIES GUIDES · NOT INDIVIDUAL BIRD LISTINGS": "EXPLORE OUR PARROTS",
    "INDIVIDUAL SPECIES GUIDE · NOT A STOCK LISTING": "SPECIES & CARE",
    "This is a species and care guide, not a listing of individual birds for sale. ": "Explore species information and everyday care. ",
    "These are species guides, not individual stock listings. ": "",
    "These are species photographs; contact Crownwing for current bird details.": "Contact Crownwing for available birds and current details.",
    "Our available range is shown below; it is not a live stock list.": "Explore our available range below.",
    "Species-gallery photographs introduce bird types. They are not listings of individual birds for sale. Request current photographs and details of the actual bird you are considering.": "Contact us for current photographs and details of the bird you are considering.",
    "Guide photographs illustrate species; they are not a live stock catalogue.": "",
    " Species-guide photos are not stock listings.": "",
    "Gallery images are not a stock list. ": "",
    " A category page is not a live stock list.": "",
    "Prepare my enquiry": "Send enquiry",
    "Download enquiry": "Send enquiry",
    "This form prepares a download; it does not send or save your details.": "Send your enquiry using the contact form.",
    "Its form creates a downloadable file; it does not send the enquiry.": "Use the contact form to send your completed enquiry.",
    "The city form only creates a downloadable copy for your own preparation; it does not send a message.": "Send your completed enquiry using our contact form.",
    "Download your enquiry and email it using the contact details provided.": "Send your enquiry using the form below.",
}


def customer_copy(text):
    for before, after in REPLACEMENTS.items():
        text = text.replace(before, after)
    text = re.sub(
        r"<figcaption>Species(?:-guide)? photograph, not (?:an?|a current) individual stock listing\.</figcaption>",
        "", text,
    )
    text = text.replace("<p>Species photographs are not individual stock listings.</p>", "")
    # Keep identification in the selected-photo caption, viewer and alt text,
    # not repeated beneath every thumbnail. Also clean older generated galleries.
    text = re.sub(
        r'(<button\b[^>]*class="photo-thumbnail"[^>]*>.*?)<span>[^<]*</span>(</button>)',
        r'\1\2', text, flags=re.S,
    )
    text = re.sub(r'<p class="enquiry-status-note">.*?</p>', "", text, flags=re.S)
    return text