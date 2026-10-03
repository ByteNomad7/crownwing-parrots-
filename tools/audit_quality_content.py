"""Audit-led practical additions; no new routes or unverified business claims."""

from buyer_resources import refresh_extension, route_file, sections
from site_config import PUBLIC_ORIGIN


ADDITIONS = {
    "/guides/buying-a-parrot-checklist/": [
        ("seller-question-sheet", "A question sheet you can use with a seller", """
<p>Keep three headings in your notes: documented facts, the keeper’s observations, and information still unknown. Ask which category each answer belongs to. An estimate can be useful, but it should not become a recorded fact simply because it appears in an advertisement.</p>
<ol>
<li><strong>Identity:</strong> What is the exact species, and what supports the identification? What scientific name is relevant to any paperwork? Is the bird in current photographs the individual under discussion?</li>
<li><strong>Age and background:</strong> Is the age recorded or estimated? What is known about previous keepers, rearing, socialisation and changes of home?</li>
<li><strong>Independent feeding:</strong> Is the bird fully weaned and eating independently? What does it actually consume, how is food presented, and what routine should initially remain familiar? Do not agree to finish weaning through hand-feeding yourself.</li>
<li><strong>Health information:</strong> What relevant history is known? Are veterinary records available, and what remains unconfirmed? A photograph or a description such as healthy is not a veterinary assessment.</li>
<li><strong>Ordinary behaviour:</strong> What does a normal day look like? Which handling does the bird choose or avoid? When does it call, and how does it respond to unfamiliar people or changes?</li>
<li><strong>Care and accommodation:</strong> What exercise, sleep and enrichment routines are familiar? What equipment and supervision will be needed in your home?</li>
<li><strong>Identification and documents:</strong> Which records or identifiers relate to this actual bird? What checks apply to this species, transaction and proposed journey, and who will resolve uncertain requirements?</li>
<li><strong>Written terms:</strong> What is the price, what is included, and what are the agreed payment, deposit, cancellation and refund terms? Do not infer an inclusion from a photograph.</li>
<li><strong>Handover and follow-up:</strong> Where and when could an agreed handover happen? Who is responsible for any proposed transport? What care information and aftercare, if any, have actually been agreed?</li>
</ol>
<p>Use the <a href="/guides/cites-parrots-uk/">UK documentation guide</a> to organise official checks, and read the <a href="/business-policies/">confirmed business policies</a> before paying. This sheet is not a certificate check, a health guarantee or a promise that every bird has the same records.</p>"""),
        ("checklist-next-decision", "Decide what must be resolved before proceeding", """
<p>Highlight answers that affect welfare, identity, cost or the feasibility of a journey. Ask for clarification rather than accepting pressure to decide during one conversation. If the keeper does not know an answer, record that uncertainty and decide what further evidence or professional advice you need.</p>
<p>Separately check your own readiness: suitable housing, familiar food, household agreement, access to an avian vet and a backup carer. The <a href="/guides/preparing-for-a-parrot/">home-preparation guide</a> covers those tasks; the <a href="/guides/buying-a-parrot/">buying cornerstone</a> explains the wider decision. Keep this shorter sheet for the seller conversation.</p>
<p>Use <a href="/contact/">the contact page</a> to send Crownwing your questions about available birds, care and proposed arrangements.</p>"""),
    ],
    "/guides/parrot-diet-nutrition/": [
        ("feeding-observation", "Observe the current diet before making a new plan", """
<p>A food list and a feeding record answer different questions. The list tells you what was offered; the record helps show what the bird actually ate. Before a handover, ask the keeper about accepted foods, usual presentation, meal timing and anything the bird regularly leaves behind.</p>
<ul><li>Record the familiar food and how it is offered, rather than assuming a mixed bowl is consumed evenly.</li>
<li>Note appetite and behaviour in the bird’s ordinary routine. Treat a change as something to discuss, not proof that a new food has been accepted.</li>
<li>Ask about existing veterinary nutrition advice and any known needs connected to species, age or health.</li>
<li>Keep the first routine familiar while arranging a suitable, bird-specific feeding plan.</li></ul>
<p>For example, a bowl containing several ingredients does not establish that each ingredient is eaten. A seed husk is also not an uneaten seed. Ask how the current keeper checks consumption before using the apparent contents of a bowl to make a decision.</p>"""),
        ("feeding-hygiene", "Make food handling part of everyday care", """
<p>Provide clean drinking water and clean food and water containers. Prepare fresh foods hygienically, check them for spoilage and remove leftovers before they become unsafe. Store food appropriately and keep it away from cleaning chemicals, pests and contamination. Suitable timing depends on the food and conditions, not one universal schedule.</p>
<p>Do not share unfamiliar household foods simply because they are safe for people. Avocado must not be offered. Check uncertain foods with a reliable bird-care source or an avian vet, and keep preparation surfaces and equipment clean. A treat should not displace the diet the bird needs.</p>
<p>Parrots have different feeding requirements, so neither an all-purpose menu nor a percentage copied from another species is a complete diet plan. The <a href="https://www.rspca.org.uk/adviceandwelfare/pets/birds/diet">RSPCA’s bird-feeding guidance</a> provides a welfare starting point; discuss the exact species and individual with an avian vet.</p>"""),
        ("nutrition-vet-questions", "Questions for a feeding-plan review", """
<ul><li>Is the diet appropriate for this identified species, life stage and known health history?</li>
<li>Which parts of the current diet should remain familiar, and how should any change be introduced and monitored?</li>
<li>How should intake and body condition be assessed for this individual?</li>
<li>Are any supplements actually indicated? Do not add them or change a prescribed plan without appropriate advice.</li>
<li>What change in appetite or behaviour warrants a prompt call to the practice?</li></ul>
<p>Do not withhold familiar food to force a reluctant bird to accept a replacement. If intake falls or the bird seems unwell, contact an avian veterinary practice promptly rather than continuing an online diet experiment. This guide is preparation for that conversation, not diagnosis or a treatment plan.</p>
<p>Sources checked: 2026-10-02. This is an editorial reference check, not veterinary review. Connect the feeding plan with <a href="/guides/preparing-for-a-parrot/">arrival preparation</a> and the <a href="/guides/parrot-ownership-costs/">ongoing food and care budget</a>.</p>"""),
    ],
    "/guides/parrot-housing-enrichment/": [
        ("enclosure-screening", "Screen the enclosure and the room together", """
<p>There is no single cage measurement suitable for every parrot. Start with the exact species, adult scale and the number of birds, then assess usable movement space with the planned fittings in place. A tall cage packed with equipment may leave less useful room than its external dimensions suggest.</p>
<ul><li>Can the bird move, turn and use its wings without repeatedly meeting hard fittings? How will climbing and supervised exercise be provided?</li>
<li>Are bar spacing, perch sizes and fittings suitable for this species, without trapping the head, feet or beak?</li>
<li>Are doors and food access points secure, and can a keeper clean and inspect every part safely?</li>
<li>Are surfaces and equipment bird-safe, intact and free of sharp edges, rust or damaged parts? Ask the supplier about materials rather than assuming a product label proves suitability.</li>
<li>Is the location away from cooking hazards, smoke, excessive heat and draughts, with room for rest as well as household activity?</li></ul>
<p>The <a href="https://www.rspca.org.uk/adviceandwelfare/pets/birds/environment">RSPCA’s bird-environment guidance</a> distinguishes individual and group accommodation. Compatible small flock birds and large non-colony parrots are not interchangeable housing cases. Do not house unfamiliar birds together simply to save space; seek suitable professional advice.</p>"""),
        ("enrichment-review", "Plan opportunities, then observe whether they work", """
<p>Enrichment is not measured by how many toys fit into a cage. Give the bird appropriate opportunities to forage, chew, climb, explore and rest, while keeping access to familiar resources predictable. Choose activities for the bird’s size, beak strength and experience.</p>
<ul><li><strong>Foraging:</strong> begin with an accessible activity the bird understands, using suitable food without restricting its essential meals.</li>
<li><strong>Chewing and climbing:</strong> check materials, fittings and wear. Replace damaged items; inspect loose threads, small parts and openings that could entangle or be swallowed.</li>
<li><strong>Movement:</strong> arrange secure supervised routes and landing/perching opportunities. Close unsafe access points and keep fans and other hazards out of use.</li>
<li><strong>Choice and rest:</strong> offer a place to withdraw from attention. More stimulation is not automatically better if the bird avoids it or cannot settle.</li></ul>
<p>Use a simple observation note: what you offered, whether the bird used it, how it responded and what needs changing. Introduce unfamiliar items thoughtfully rather than replacing the whole environment at once. The <a href="https://www.rspca.org.uk/adviceandwelfare/pets/birds/enrichment">RSPCA enrichment advice</a> explains the welfare purpose behind these activities.</p>"""),
        ("exercise-and-maintenance", "Make exercise and maintenance repeatable", """
<p>Before each supervised session, check doors, windows, fans, electrical leads and access by other animals. Agree who is supervising and how the bird returns safely to its enclosure. Do not assume a room is secure because it worked on a previous day.</p>
<p>Include cleaning, checks of perches and fasteners, and replacement of worn equipment in the <a href="/guides/parrot-ownership-costs/">ownership budget</a>. If considering outdoor access or an aviary, check the <a href="/guides/cites-parrots-uk/">relevant keeper-registration and official rules</a> rather than applying indoor-home assumptions.</p>
<p>Sources checked: 2026-10-02. Editorial source checks are not a professional assessment of your enclosure. Use the <a href="/guides/preparing-for-a-parrot/">home-safety checklist</a> and specific species information before making a purchase.</p>"""),
    ],
    "/guides/preparing-for-a-parrot/": [
        ("before-handover-checklist", "Before-handover readiness checklist", """
<ul><li>Confirm the individual bird’s identity, established foods, daily routine and any care information you will receive.</li>
<li>Set up species-appropriate accommodation, safe perches, feeding equipment and water before the journey.</li>
<li>Agree household supervision, door/window security and how other animals will be kept apart.</li>
<li>Identify an avian veterinary practice, its contact details and how to obtain urgent advice outside normal hours.</li>
<li>If you already keep birds, discuss separate accommodation and any quarantine or introduction plan with appropriate professional support; do not improvise immediate mixing.</li>
<li>Confirm the actual handover location, timing, suitable carrier and who is responsible for any proposed transport. Do not treat a website city name as a delivery agreement.</li>
<li>Resolve the individual price, records and written terms using the <a href="/guides/buying-a-parrot-checklist/">seller-question sheet</a> before paying or travelling.</li></ul>
<p>Have a backup plan if a journey is delayed or a household carer is unavailable. Readiness means the ordinary care can continue, not just that supplies have been bought.</p>"""),
        ("room-hazard-checklist", "Review hazards before opening the carrier", """
<p>Bird-proofing involves air as well as surfaces. Heated non-stick materials and some household appliances can release dangerous fumes; smoke, sprays and other airborne hazards also matter. Do not rely on the absence of a noticeable smell as a safety test.</p>
<ul><li>Keep the bird away from cooking fumes, smoke, aerosols and cleaning-product exposure. Review heated equipment before use.</li>
<li>Secure windows and doors and switch off fans before supervised activity. Assess glass, mirrors and other collision risks.</li>
<li>Remove access to electrical leads, hot surfaces, unsafe foods, chemicals and objects that could be chewed or swallowed.</li>
<li>Keep other pets separated unless an appropriate supervised arrangement has been carefully established.</li>
<li>Choose a rest area and explain boundaries to children and visitors; the bird must be able to avoid attention.</li></ul>
<p>The veterinary-authored <a href="https://vcahospitals.com/lakeline/know-your-pet/household-hazards-and-dangers-to-birds">VCA household-hazards guide</a> explains why these checks matter. Suspected exposure to toxic fumes calls for urgent veterinary advice; do not wait for an online checklist to settle a health concern.</p>"""),
        ("arrival-information", "Keep arrival quiet and information usable", """
<p>Place food, water and familiar resources where the bird can access them. Let it observe the new surroundings without a queue of visitors, forced handling or expectations of immediate speech or affection. Keep the routine predictable while learning its responses.</p>
<p>Keep the agreed care information together: identity, known history, feeding routine, any relevant records and the seller’s actual follow-up arrangements. Record uncertainties rather than filling them with assumptions. Observe appetite and ordinary activity, and contact an avian vet promptly if the bird appears unwell.</p>
<p>The first week is an observation period, not a deadline for trust or tameness. Read the <a href="/guides/buying-a-parrot/">buying guide’s arrival and first-week section</a>, <a href="/guides/parrot-diet-nutrition/">feeding guidance</a> and <a href="/guides/parrot-housing-enrichment/">safe housing plan</a> rather than changing every aspect of care simultaneously.</p>
<p>Sources checked: 2026-10-02. This is an editorial source check, not veterinary review or an assessment of your home.</p>"""),
    ],
    "/parrot-prices-uk/": [
        ("purchase-quote-record", "Compare the quotation, not just its headline amount", """
<p>Request a written quotation identifying the particular bird. An amount without identity and terms is not a like-for-like comparison. Record the exact species, known age or stated age uncertainty, quotation date and what information supports the bird’s identity. Ask how long a proposal remains valid rather than assuming it reserves an individual.</p>
<ul><li><strong>Bird and records:</strong> Which individual does the quote identify, and which care information or documents are included?</li>
<li><strong>Equipment:</strong> Is any enclosure, carrier, food or other equipment included? If so, check suitability and condition separately.</li>
<li><strong>Payment:</strong> What total and payment method are agreed? If a deposit is proposed, what does it reserve and how do the confirmed terms apply?</li>
<li><strong>Handover:</strong> What location and timing are actually agreed? Is any transport proposed, who arranges it and is there a separately stated cost?</li>
<li><strong>Follow-up:</strong> What care information and aftercare are offered, and what is outside that agreement?</li></ul>
<p>Keep a separate list of items not included and questions still unresolved. Two quotes with different equipment, records or arrangements are not equivalent simply because they concern the same broad parrot group.</p>"""),
        ("quote-versus-budget", "Separate the seller’s amount from your ownership budget", """
<p>The purchase quote is an agreed commercial amount for an individual. Your care budget is a separate estimate built from providers and equipment suitable for your home. Include accommodation, ongoing food and enrichment, replacement equipment, veterinary support and care while you are away. A low purchase amount does not make those commitments smaller.</p>
<p>No current individual Crownwing price or verified market-average range is published here. Request a <a href="/contact/">current individual quotation</a>; do not treat an educational photograph as a priced listing. Use the <a href="/guides/parrot-ownership-costs/">ownership-cost calculator</a> for your own researched estimates, not a forecast of Crownwing charges.</p>
<p>Before making payment, read the <a href="/business-policies/">payment, deposit, delivery, cancellation and refund policy</a> and confirm the proposed sale’s specific terms. This comparison guide does not replace that policy, change statutory rights, promise delivery or establish a standard equipment package.</p>"""),
    ],
    "/locations/belfast/": [
        ("ni-route-record", "Create an origin-and-destination record", """
<p>A Belfast enquiry can concern a bird already in Northern Ireland or a proposed movement from elsewhere. Those are not the same situation. Before treating a journey as feasible, identify the current jurisdiction, intended destination, exact species and scientific name, purpose of movement, number of birds and proposed date.</p>
<ul><li>Where is the individual currently kept, and which parts of a proposed route cross a border or jurisdiction?</li>
<li>Is the journey connected to a sale or change of ownership, or another purpose? Do not assume guidance for an accompanied personal pet automatically covers a commercial purchase.</li>
<li>Which identification, origin and health information is available, and what remains unknown?</li>
<li>Who will ask the relevant authorities about documents, health requirements, timing and any current restrictions?</li></ul>
<p>This record organises the questions. It is not permission to move a bird, proof that documents are sufficient or confirmation that Crownwing offers a transport service.</p>"""),
        ("ni-official-sources", "Use the relevant authorities, not a general UK assumption", """
<p>DAERA’s <a href="https://www.daera-ni.gov.uk/articles/other-animal-species-movements-great-britain-northern-ireland">guidance on other animal-species movements from Great Britain to Northern Ireland</a> distinguishes movement categories and provides official starting points. Check the provisions applicable to the actual bird, purpose and route, and ask the authority to clarify uncertainties before making arrangements.</p>
<p>CITES trade documents are a separate question from animal-health movement requirements. GOV.UK’s <a href="https://www.gov.uk/guidance/cites-imports-and-exports">CITES import and export guidance</a> identifies APHA’s role and the need to consider the authorities involved. Do not treat one document as answering every requirement.</p>
<p>The <a href="/guides/cites-parrots-uk/">Crownwing UK documentation guide</a> brings these distinctions together, including keeper-registration questions. It is a practical reading aid, not an authority’s decision about a specific certificate or journey.</p>
<p>Sources checked: 2026-10-02. This is an editorial reference check, not legal, veterinary or official approval. No Belfast premises, local stock, viewing point or handover service is established by this page; confirm any individual proposal directly.</p>"""),
    ],
}


def apply_audit_quality(metadata):
    for path, records in ADDITIONS.items():
        target = route_file(path)
        marker = "audit-quality-" + path.strip("/").replace("/", "-")
        block = '<div class="content-enhancement" id="' + marker + '">' + sections(records) + "</div>"
        text = refresh_extension(target.read_text(), block, marker)
        target.write_text(metadata(text, path, PUBLIC_ORIGIN))
    target = route_file("/available-birds/")
    target.write_text(metadata(
        target.read_text(), "/available-birds/", PUBLIC_ORIGIN,
        "Available Parrot Groups UK | Enquire | Crownwing",
        "Explore Crownwing's eight offered parrot groups. Enquire for current individual bird details, photographs, ages, prices and proposed handover arrangements.",
    ))