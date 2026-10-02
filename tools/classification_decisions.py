"""Editorial decisions for the complete Crownwing audit, separate from metrics.

These are recommendations, not a deployment instruction or evidence of stock.
Do not derive a keep/merge decision from word count or textual similarity alone.
"""

DECISIONS = {}


def decision(route, classification, page_type, intent, keyword, secondary,
             strength, weakness, action, reason, priority="MEDIUM", target=None):
    DECISIONS[route] = dict(
        classification=classification, page_type=page_type, intent=intent,
        keyword=keyword, secondary=secondary, strength=strength,
        weakness=weakness, action=action, reason=reason, priority=priority,
        target=target or route,
    )


decision("/", "A", "Commercial", "Navigational / commercial investigation",
         "Crownwing Parrots UK", "UK parrot breeder; parrot retailer; Crownwing species",
         "Distinct brand introduction, eight actual offered groups, buyer and species pathways.",
         "Independent credentials and individual-bird details are not established by the homepage.",
         "Keep the branded nature-led H1; strengthen links to the buying guide, policies and current group enquiries.",
         "The homepage establishes the business rather than duplicating a national sales landing page.", "HIGH")
decision("/available-birds/", "A", "Commercial", "Navigational / availability enquiry",
         "Crownwing available parrots", "available parrot groups; current bird enquiry",
         "Clear eight-group availability and an explicit individual-details-by-enquiry boundary.",
         "No live individual stock, ages or prices; a title promising those details can imply more than the page supplies.",
         "Keep a branded range/enquiry role; make metadata explicitly about offered groups and individual details by enquiry.",
         "A branded availability directory has a different job from the national buying hub.", "HIGH")
decision("/contact/", "A", "Other", "Navigational / support",
         "contact Crownwing Parrots", "parrot enquiry; downloadable enquiry; contact details",
         "Direct contact routes and an honest explanation that the form downloads rather than sends.",
         "The buyer must manually send the file; this is not a working online submission service.",
         "Keep concise and easy to reach; preserve the download-only disclosure and direct email options.",
         "A short contact page can fully satisfy its purpose; word count is not a removal criterion.", "HIGH")
for route, keyword, strength in [
    ("/business-policies/", "Crownwing payments delivery cancellation policy",
     "Owner-confirmed deposit, payment and refund terms; non-excludable consumer-rights caveat."),
    ("/privacy-policy/", "Crownwing privacy policy",
     "Describes local-only forms, actual data handling and the absence of online account/payment processing."),
    ("/cookie-policy/", "Crownwing cookie policy",
     "Explains external font requests, local enquiry downloads and the current lack of optional tracking."),
]:
    decision(route, "A", "Policy", "Trust/business / support", keyword,
             "business contact; consumer information; Crownwing terms", strength,
             "Owner/legal review is still required; an audit is not legal approval.",
             "Preserve confirmed terms and dated notices; keep policy links prominent without splitting them into thin keyword pages.",
             "Independent trust/support value justifies retaining the URL.", "HIGH")
decision("/our-approach/", "B", "Other", "Trust/business / commercial investigation",
         "about Crownwing Parrots", "parrot breeder and retailer; buying process; aftercare questions",
         "Truthful breeder/retailer identity and sensible questions about origin, records and handover.",
         "Much of the body says what to ask, not who operates the business or what Crownwing actually commits to providing.",
         "Expand with owner-confirmed business identity, real care practices and precisely scoped buying/aftercare process; do not invent years, credentials or services.",
         "An about/process page needs verified first-party evidence beyond a generic buying checklist.", "HIGH")
decision("/parrot-prices-uk/", "B", "Commercial", "Commercial investigation",
         "parrot prices UK", "how much does a parrot cost UK; purchase quotation; price inclusions",
         "Separates an individual quote from lifetime care and avoids invented prices.",
         "It neither gives verified prices nor a detailed quote-comparison worksheet; price-search satisfaction remains partial.",
         "Add a useful purchase-quote comparison and inclusion/exclusion checklist. Add real prices or ranges only after owner verification; link to the separate ownership budget.",
         "Purchase-price intent differs from ongoing ownership-cost intent and deserves a stronger existing URL.", "HIGH")
decision("/guides/", "A", "Guide", "Navigational / informational discovery",
         "parrot buying and care guides UK", "buyer resource library; UK parrot paperwork; care guides",
         "An organised library spanning buying, care and documentation, with ordinary HTML links.",
         "It must remain a directory rather than becoming a second buying article or a stock page.",
         "Keep the library role; absorb useful regional-discovery navigation if location merges are approved.",
         "A resource index need not have article-length prose to earn its place.")
decision("/parrot-care/", "A", "Guide", "Informational discovery",
         "parrot care guides", "diet guide; accommodation guide; ownership planning",
         "Direct, focused navigation to essential care resources.",
         "Short main copy, but this is a hub rather than an incomplete standalone care textbook.",
         "Keep as the focused care entry point, linked within the broader buyer library; avoid duplicating its articles.",
         "Its narrower care-navigation purpose distinguishes it from the complete guides library.")
decision("/guides/buying-a-parrot/", "A", "Guide", "Informational / commercial investigation",
         "how to buy a parrot UK", "seller questions; buyer warning signs; weaning; first week; documentation",
         "A substantive buying journey including health questions, background, terms, preparation and first-week checks.",
         "No expert-review claim should be inferred; current individual-bird and service facts remain by enquiry.",
         "Maintain as the buyer cornerstone; add relevant contextual links and preserve the manual-send explanation.",
         "Comprehensive decision/process intent is different from the commercial range hub.", "HIGH")
decision("/guides/choosing-a-parrot/", "A", "Guide", "Commercial investigation / informational",
         "which parrot should I get", "best parrot for first time owner; household fit; noise; species comparison",
         "Eight-group, ten-facet comparison, readable without JavaScript and without ranking a species as universally easy.",
         "Broad groups cannot establish exact-species or individual behaviour.",
         "Keep the comparison; merge genuinely useful household-planning sections from city pages only after approval.",
         "An actionable comparison serves a distinct shortlist decision.", "HIGH")
decision("/guides/parrot-ownership-costs/", "A", "Guide", "Informational / commercial investigation",
         "cost of keeping a parrot UK", "monthly parrot costs; lifetime budget; setup costs; emergency reserve",
         "Separates setup, recurring and uncertain costs and offers a local-only blank-estimate calculator.",
         "No market-average price figures or guarantee of future costs; users must obtain their own estimates.",
         "Keep the independent cost role and safe calculator; strengthen backup-care and quote-source prompts, not invented figures.",
         "A personal ownership budget is not a duplicate of a purchase-price page.", "HIGH")
decision("/guides/cites-parrots-uk/", "A", "Guide", "Regulatory/legal information",
         "CITES parrots UK", "Article 10; parrot documentation; bird keeper registration; GB NI movement",
         "Official references and a genuine source-check date; separates transaction, identification, border and housing rules.",
         "Editorial checks are not professional advice or verification of a specific bird/certificate.",
         "Keep this regulatory cornerstone; route documentation queries here and recheck official references before changing claims.",
         "Jurisdiction-sensitive documentation is a real UK buyer need and should not be fragmented into near-duplicate pages.", "HIGH")
for route, keyword, secondary, strength, gap, action in [
    ("/guides/buying-a-parrot-checklist/", "questions to ask a parrot breeder",
     "parrot buying checklist; records; weaning; payment questions",
     "Useful stages covering identity, diet, behaviour, terms and preparation.",
     "Narrative prompts are not yet a practical question-by-question, recordable checklist.",
     "Add concrete seller questions and spaces/categories for documented, observed and unknown answers; keep it a usable checklist, not another cornerstone article."),
    ("/guides/parrot-diet-nutrition/", "parrot diet",
     "safe parrot food; changing diet; species nutrition; food hygiene",
     "Warns about food selection, species differences, abrupt changes and avocado; links to RSPCA feeding advice.",
     "Readers lack a practical feeding-observation example, food-handling routine and a structured set of veterinary nutrition questions.",
     "Expand species-sensitive observation, food safety and gradual-change planning using welfare/veterinary sources; no universal percentages or supplement prescriptions."),
    ("/guides/parrot-housing-enrichment/", "parrot cage size",
     "safe parrot cage; enrichment; parrot toys; exercise; cage placement",
     "Prioritises usable space, activity, safety and replacement rather than a decorative cage.",
     "No practical enclosure/equipment-screening checklist or concrete enrichment-planning examples.",
     "Add room/cage/hardware screening, species-dependent movement examples, supervised activity and a sample enrichment review; avoid one cage size for every species."),
    ("/guides/preparing-for-a-parrot/", "preparing a home for a parrot",
     "parrot home hazards; before handover; first week; veterinary preparation",
     "Covers readiness, household hazards, finding an avian vet and gradual adjustment.",
     "Preparation is broad; readers need a workable before-handover and arrival checklist and a clear route for concerns.",
     "Expand a source-backed room-safety checklist, handover-information list, quiet arrival plan and monitoring/vet-contact prompts; avoid duplicating the whole buying guide."),
]:
    decision(route, "B", "Guide", "Informational", keyword, secondary, strength, gap, action,
             "Standalone practical intent is useful, but the present broad guidance leaves concrete reader tasks unfinished.", "HIGH")
decision("/locations/belfast/", "B", "Other", "Regulatory/legal / buyer investigation",
         "parrot movement Great Britain Northern Ireland", "Belfast parrot enquiry; origin and destination; NI documentation",
         "Recognises Northern Ireland and asks for origin/destination before discussing any journey.",
         "The body lacks direct authoritative movement references and a source-check note; its generic household sections need tighter scope.",
         "Retain only as a scoped Belfast/NI enquiry and movement-check aid: add official DAERA/APHA sources, connect to the main documentation guide and obtain owner confirmation of any proposed arrangement.",
         "NI movement is materially different from generic Great Britain household planning; no branch or transport service is established.", "HIGH")

city_merges = [
    ("birmingham", "household agreement and responsibilities", "/guides/choosing-a-parrot/", "which parrot should I get"),
    ("bristol", "room safety and repeatable exercise", "/guides/preparing-for-a-parrot/", "preparing a home for a parrot"),
    ("cardiff", "household-based species shortlisting", "/guides/choosing-a-parrot/", "which parrot should I get"),
    ("edinburgh", "continuity of care and backup planning", "/guides/parrot-ownership-costs/", "cost of keeping a parrot UK"),
    ("glasgow", "established feeding routines", "/guides/parrot-diet-nutrition/", "parrot diet"),
    ("leeds", "usable accommodation and equipment resources", "/guides/parrot-housing-enrichment/", "parrot cage size"),
    ("liverpool", "individual identity and recorded background", "/guides/buying-a-parrot-checklist/", "questions to ask a parrot breeder"),
    ("london", "usable space and shared living", "/guides/choosing-a-parrot/", "which parrot should I get"),
    ("manchester", "weekly care timetable and substitute carers", "/guides/choosing-a-parrot/", "which parrot should I get"),
    ("newcastle", "confirmed identity, terms and handover logistics", "/guides/buying-a-parrot-checklist/", "questions to ask a parrot breeder"),
    ("nottingham", "first-time expectations and individual suitability", "/guides/choosing-a-parrot/", "which parrot should I get"),
    ("sheffield", "foraging, rest and supervised exercise", "/guides/parrot-housing-enrichment/", "parrot enrichment"),
]
for city, topic, target, keyword in city_merges:
    decision("/locations/" + city + "/", "C", "Other", "Commercial investigation / informational; local framing",
             keyword, topic + "; city enquiry preparation",
             "Distinct useful discussion of " + topic + "; does not claim a branch or automatic delivery.",
             "The planning advice applies outside this city. A geographical introduction and a download form do not demonstrate unique local buyer information or operations.",
             "Preserve the useful " + topic + " material in " + target +
             "; replace city-directory links with relevant resources/contact; then issue a single-hop 301 only after owner approval and production-host redirect support.",
             "Merge for overlapping reader tasks, not because the prose is an exact duplicate. No verified city-specific service, stock or local resource justifies this separate search landing page.",
             "HIGH", target)
decision("/locations/", "C", "Other", "Navigational / local-framed resource discovery",
         "parrot buyer guides UK", "regional enquiries; household planning; Northern Ireland checks",
         "A clear directory with honest local-service disclaimers.",
         "Its independent purpose shrinks if the twelve generic Great Britain city guides are merged.",
         "Move useful discovery copy and the Belfast/NI link to /guides/; use /contact/ for location-specific enquiry details; retire the directory through a tested 301 only with approval.",
         "The broader guides library is the strongest replacement for resource discovery, without presenting unverified coverage as local service.",
         "HIGH", "/guides/")

decision("/parrots/", "A", "Species", "Informational discovery / commercial investigation",
         "parrot species guide", "compare parrot groups; Crownwing collection; parrot characteristics",
         "Eight-group educational collection leading to distinct species profiles and buying routes.",
         "An educational gallery does not confirm an exact species or individual is for sale.",
         "Keep the educational overview; retain ordinary links to group care pages and clearly distinguish the commercial hub.",
         "A species-research directory has a different purpose from an available-group or buying directory.")

families = [
    ("african-parrots", "african-grey-parrots", "African grey", "Congo/Timneh identification, sensitivity and routine"),
    ("amazons", "amazon-parrots", "Amazon", "species variation, calls, excitement and handling boundaries"),
    ("caiques", "caiques", "Caique", "physical play, supervision and energetic interaction"),
    ("cockatoos", "cockatoos", "Cockatoo", "species scale, feather dust, calls and independent activity"),
    ("conures", "conures", "Conure", "green-cheeked/sun contrasts and noise relative to body size"),
    ("eclectus", "eclectus-parrots", "Eclectus", "identity, plumage, individual preferences and feeding routine"),
    ("macaws", "macaws", "Macaw", "mini/large variation, powerful beaks and usable movement space"),
    ("parakeets-small-psittacines", "parakeets-small-parrots", "Budgie and parakeet", "flock/social differences, flight and exact-species equipment"),
]
for info_slug, sales_slug, name, detail in families:
    decision("/parrots/" + info_slug + "/", "A", "Species", "Informational / commercial investigation",
             name.lower() + " parrot care" if name != "Budgie and parakeet" else "budgie and parakeet care",
             name + " lifespan; temperament; diet; noise; housing; species comparison",
             "Substantial group overview with " + detail + " and links to specific educational profiles.",
             "Broad-group guidance cannot replace a species-specific care assessment; sourcing and numerical claims need editorial verification.",
             "Retain the group overview; strengthen verified references and contextual links to diet, housing, costs and documentation without duplicating the buying page.",
             "An offered group has an independent research intent and meaningful differences from other groups.")
    decision("/parrots-for-sale/" + sales_slug + "/", "A", "Commercial", "Transactional enquiry / commercial investigation",
             name.lower() + " parrots for sale UK" if name != "Budgie and parakeet" else "budgies and parakeets for sale UK",
             name + " availability; individual price; rearing history; buyer questions; handover",
             "Offered group confirmed by the owner, with group-specific buying questions about " + detail + ".",
             "Exact species, individuals, price, rearing and any handover service remain unconfirmed until enquiry.",
             "Keep the buying intent; make links to the checklist, price guidance and documentation explicit; never invent listings or Product availability.",
             "A purchase enquiry page is distinct from a group's educational care overview.", "HIGH")
decision("/parrots-for-sale/", "A", "Commercial", "Transactional enquiry / commercial investigation",
         "parrots for sale UK", "parrot for sale UK; buy a parrot UK; pet parrots; Crownwing offered groups",
         "Existing national commercial hub, eight offered groups, buying steps, individual enquiry and policy links.",
         "No live individual stock; payment/delivery claims must stay within confirmed policies.",
         "Strengthen this established canonical instead of creating /parrots-for-sale-uk/ as a duplicate. Link directly to buyer, documentation and policy resources.",
         "The requested UK commercial hub already exists under a stable, relevant URL.", "HIGH")
for slug, keyword, detail in [
    ("small-parrots", "small parrots for sale UK", "budgie/lovebird/conure/caique differences, flight and social planning"),
    ("large-parrots", "large parrots for sale UK", "macaw/cockatoo/Amazon differences, tail clearance, dust and robust equipment"),
    ("talking-parrots", "talking parrots UK", "learned speech versus natural calls, context and no guaranteed vocabulary"),
]:
    decision("/parrots-for-sale/" + slug + "/", "A", "Commercial", "Commercial investigation",
             keyword, detail + "; species comparison; individual enquiry",
             "A genuine cross-group choice filter with specific " + detail + ".",
             "Not a stock list or guaranteed-trait offer; must not duplicate a general species-selection article.",
             "Keep the distinct buyer filter and its group links; preserve variation caveats and truthful individual enquiry.",
             "Size or vocal-learning criteria span several groups and have a separate reader decision, not just a keyword variation.")

individuals = [
    ("african-parrots/congo-african-grey-parrot", "Congo African grey", "grey feather edging, red tail and Congo/Timneh distinctions", "Trace size/lifespan claims to credible references and add concrete routine/sensitivity questions and documentation identification prompts."),
    ("african-parrots/timneh-parrot", "Timneh parrot", "maroon tail, horn-coloured bill and smaller adult scale", "Reference current Psittacus timneh taxonomy and develop practical movement, routine and individual-history comparisons with Congo greys."),
    ("amazons/blue-fronted-amazon-parrot", "Blue-fronted Amazon", "variable blue forehead/yellow facial markings and expressive calls", "Source anatomy/lifespan claims and develop excitement, handling-boundary and household-noise planning rather than broad 'social bird' advice."),
    ("amazons/yellow-naped-amazon-parrot", "Yellow-naped Amazon", "yellow nape, robust build and strong vocal/social commitment", "Source species identity and long-term claims; connect exact scientific identification to the official documentation-check process without assuming a universal certificate rule."),
    ("caiques/black-headed-caique", "Black-headed caique", "black cap, stocky shape and energetic physical play", "Add sourced identification and concrete safe-play/supervision planning, including questions about interaction with other birds rather than assumed compatibility."),
    ("caiques/white-bellied-caique", "White-bellied caique", "orange head, pale belly and explicit taxonomic ambiguity", "Verify the Pionites leucogaster treatment and add a practical activity/supervision plan and individual identification questions; do not treat all regional forms as interchangeable."),
    ("cockatoos/galah-cockatoo", "Galah cockatoo", "rose/grey markings, smaller cockatoo scale and lively social needs", "Add referenced species information and specific nutrition/body-condition questions for an avian vet, with independent-activity and equipment planning; no medical or universal-diet prescription."),
    ("cockatoos/umbrella-cockatoo", "Umbrella cockatoo", "broad white crest, strong chewing and substantial social demands", "Source adult scale/lifetime claims and develop usable movement, feather-dust/cleaning and independent-activity household checks."),
    ("conures/green-cheeked-conure", "Green-cheeked conure", "maroon tail, colour mutations and compact climbing/flight needs", "Add referenced identity/range information and concrete small-bird equipment and daily exercise checks; compare noise with the Sun Conure without promising quietness."),
    ("conures/sun-conure", "Sun conure", "age-related colour changes and a piercing voice despite small size", "Add referenced species facts and an actionable neighbour/noise and supervised-activity assessment; no guaranteed temperament, speech or numerical noise promise."),
    ("eclectus/papuan-eclectus-parrot", "Papuan Eclectus parrot", "sexual plumage differences and an Avibase-backed polychloros/roratus distinction", "Build on the real taxonomy reference with source-backed feeding-observation, safe accommodation and veterinary discussion prompts; do not invent sex-based temperament or fixed nutrient rules."),
    ("macaws/blue-and-gold-macaw", "Blue and gold macaw", "blue/gold colours, facial feather lines, tail clearance and powerful beak", "Source size/lifetime information and develop room/landing-route, robust-equipment and transport questions linked to the ownership budget."),
    ("macaws/scarlet-macaw", "Scarlet macaw", "red body, yellow/blue wing panels and extensive space commitment", "Reference species identification and add actionable tail/wing-clearance, household-boundary and long-term-care planning rather than generic large-parrot advice."),
    ("parakeets-small-psittacines/budgerigar", "Budgerigar", "cere/age/colour caveats, flock behaviour and usable flight space", "Add authoritative welfare references and practical social/flight/enclosure checks; discuss companion arrangements with suitable expert guidance rather than treating human attention as universally equivalent."),
    ("parakeets-small-psittacines/indian-ringneck-parakeet", "Indian ringneck parakeet", "long tail, red bill and age/sex-dependent neck ring", "Source identity and lifespan statements and develop patient socialisation, flight and individual-history questions; neck-ring appearance is not a complete sex record."),
    ("parakeets-small-psittacines/peach-faced-lovebird", "Peach-faced lovebird", "short tail, peach face, colour variation and confident social boundaries", "Reference identification and social-welfare claims; add practical safe movement, companion-history and supervised-interaction planning without assuming pair compatibility."),
]
for slug, name, detail, expansion in individuals:
    decision("/parrots/" + slug + "/", "B", "Species", "Informational / species-specific buyer investigation",
             name.lower() + " care", name + " size; lifespan; temperament; diet; housing; suitability",
             "Distinct anatomy and ownership discussion: " + detail + "; visibly an educational profile, not a stock listing.",
             "A useful introduction, but most care sections remain broad and numerical/species claims are not consistently sourced. Exact offered-species scope is not independently confirmed by a gallery.",
             expansion + " Confirm with the owner that this exact species belongs in Crownwing's intended offered range before treating it as a commercial target; keep stock claims separate.",
             "Improve evidence and species-specific reader tasks, not length. Do not use an unconfirmed profile as proof of availability; if the owner excludes the species, reassess retention rather than invent an offer.")