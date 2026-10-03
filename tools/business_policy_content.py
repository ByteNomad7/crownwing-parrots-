"""Owner-confirmed, enquiry-site policies; no invented commercial guarantees.

Privacy sections follow the ICO's Article 13 information checklist. Sales
sections follow the owner's supplied terms and GOV.UK distance-selling guidance.
Unspecified commercial terms must be agreed before payment, not fabricated.
"""

UPDATED = "3 October 2026"

POLICIES = {
    "/privacy-policy/": {
        "title": "Privacy Policy",
        "description": "How Crownwing Parrots handles website visits, contact-form enquiries and email correspondence, including retention criteria and your UK privacy rights.",
        "intro": "Understand what happens to your information when you browse this website, prepare an enquiry or contact Crownwing Parrots.",
        "sections": [
            ("controller", "Who is responsible for your information?", [
                "Crownwing Parrots is a sole-trader business and is responsible for the personal information it uses to handle enquiries and customer correspondence. Use the business address and email contacts below for privacy questions or requests about your information.",
                "This notice covers the current enquiry website and information you choose to send to the business. It does not describe an online checkout, customer-account system or newsletter service, because those facilities are not provided on this website.",
            ]),
            ("information", "Information you provide", [
                "When you email us, we receive your email address, the name and contact details you provide, your message and any attachments. An enquiry may include the species you are interested in, your location, experience, proposed home and care arrangements. Please provide only information relevant to the enquiry and avoid sending sensitive personal information unnecessarily.",
                "If an enquiry progresses to a purchase, additional information may be needed for the quotation, invoice, sales agreement, agreed handover and any legally required records. The information requested should be relevant to those purposes; do not send card details, passwords or banking credentials by email.",
            ]),
            ("enquiry-forms", "Contact-form enquiries", [
                "When you submit the contact form, your name, email address, selected bird interest and message are sent to Netlify Forms, which processes and stores submissions for Crownwing Parrots. Crownwing uses this information to respond to your enquiry. Submitting the form does not subscribe you to marketing.",
                "Netlify provides submission handling and spam filtering. Form submissions may also be sent to the business by email where submission notifications are enabled. You can contact us using the published email addresses instead of the form. Please avoid including unnecessary sensitive information in either channel.",
            ]),
            ("technical-information", "Information involved in website visits", [
                "Serving a web page involves technical information such as your IP address, the requested page, time of the request and browser or device information. The hosting infrastructure may handle this information in access or security logs to deliver the site, investigate errors and protect the service.",
                "The website also requests typefaces from Google Fonts. These requests can disclose your IP address, browser information and the referring website to Google. Fonts are not an analytics service, but an external font request is still a disclosure of technical information. See our Cookie Policy and the provider information linked below.",
            ]),
            ("purposes-bases", "Why information is used and the lawful bases", [
                "We use enquiry information to answer your questions, identify the bird or information you are asking about and discuss a possible purchase. Where this involves steps you request before entering a contract, the lawful basis is taking steps at your request prior to a contract; information necessary to fulfil an agreed sale is used for performance of that contract.",
                "For general correspondence, handling concerns and keeping the website secure, the relevant basis is legitimate interests: communicating with prospective customers, resolving issues and protecting the service. Those interests must be balanced against your rights and reasonable expectations.",
                "Where a record must be kept or information disclosed to comply with an applicable legal obligation, that obligation is the lawful basis. The current website does not subscribe you to marketing or use a consent checkbox as blanket permission for unrelated processing.",
            ]),
            ("sharing", "Who may receive information", [
                "Website hosting and email-service providers handle information necessary to provide their services. Netlify handles contact-form submissions on our behalf. Gmail is used where correspondence is sent to or from our Gmail address. Your own email provider also handles messages you send; the provider for another mailbox may differ.",
                "If a sale requires information to be shared with an agreed transport provider, veterinary professional or authority, the relevant purpose and information should be explained as part of those arrangements. Personal information may also need to be disclosed where required by law. An enquiry alone does not authorise unrelated disclosure.",
            ]),
            ("international", "Services outside the United Kingdom", [
                "Email, hosting and external-font services may involve processing outside the United Kingdom. The location and safeguards depend on the service and its terms. Google explains its own handling of Google Fonts requests in the information linked below.",
                "You may contact us to ask which providers handle the information in your correspondence and for information about any applicable international-transfer safeguards. A provider’s privacy statement does not itself replace the business’s responsibility to establish an appropriate basis for a restricted transfer.",
            ]),
            ("retention", "How retention is determined", [
                "A fixed retention schedule has not yet been set for contact-form submissions, enquiry emails and customer records. Retention must therefore be assessed against the purpose of the record, rather than keeping every enquiry indefinitely or promising an unsupported deletion deadline.",
                "The relevant criteria are whether an enquiry is still active or needs reasonable follow-up, whether a sale or complaint remains unresolved, whether a record is required for accounting or another legal obligation, and whether it is needed for the establishment, exercise or defence of legal claims. Once those purposes no longer justify keeping personal information, it should be deleted or anonymised.",
                "Ask us about the criteria applied to a particular record or request deletion using the contacts below. Hosting and email-provider logs may have separate retention arrangements. Requests concerning a form enquiry should cover the submission stored in Netlify Forms and any associated email correspondence.",
            ]),
            ("rights", "Your information rights", [
                "Depending on the circumstances and lawful basis, you may request access to your personal information, correction of inaccurate information, erasure, restriction of processing or a portable copy of information. These rights are not absolute; for example, some records may need to be retained to meet a legal obligation.",
                "Right to object: you can object to processing based on legitimate interests, explaining your particular situation. Any objection must be considered under the applicable rules. If consent is used for a future optional activity, you may withdraw it without affecting the lawfulness of earlier processing.",
                "Email us with your request and enough information to identify the relevant correspondence. We may need proportionate confirmation of identity before disclosing personal information. Requests are normally answered within one month, subject to the extensions and other rules allowed by applicable law.",
            ]),
            ("choice-security", "Your choices and security", [
                "You can browse the public pages without completing an enquiry form. Contact information is necessary if you want a reply, and an agreed purchase may require particular details for the contract or legal records. We should explain why additional information is needed when requesting it.",
                "The website does not make automated decisions with legal or similarly significant effects about visitors. Please use the published email addresses and avoid sending unnecessary sensitive documents. No website or email service can guarantee absolute security.",
            ]),
            ("complaints-updates", "Questions, complaints and changes", [
                "Contact Crownwing Parrots first if you have a concern about how your information is handled. You also have the right to complain to the UK Information Commissioner’s Office at ico.org.uk; you do not have to wait for a business complaint process to finish before contacting the regulator.",
                "This notice will need review if the website introduces online payments, accounts, analytics, advertising or other new data uses. The update date identifies the version currently displayed; it does not imply that an external regulator has approved this notice.",
            ]),
        ],
        "references": [
            ("https://ico.org.uk/make-a-complaint/", "ICO: make a data-protection complaint"),
            ("https://developers.google.com/fonts/faq/privacy", "Google Fonts privacy information"),
            ("https://policies.google.com/privacy", "Google Privacy Policy"),
        ],
    },
    "/cookie-policy/": {
        "title": "Cookie Policy",
        "description": "Information about cookies, browser storage, external Google Fonts and contact-form submissions on the Crownwing Parrots website.",
        "intro": "A clear explanation of browser storage and external services used by the current Crownwing Parrots website.",
        "sections": [
            ("cookies", "Cookies and similar technologies", [
                "Cookies are small pieces of information stored by a browser for a website. Similar technologies include local storage and session storage. These can support necessary functions or optional activities such as measuring visits and advertising.",
            ]),
            ("current-use", "What the website currently uses", [
                "The current site’s own code does not set cookies or store enquiry details in local storage or session storage. It does not contain Google Analytics, advertising pixels, a newsletter tracker or a shopping basket. Browsing and submitting an enquiry do not require accepting optional tracking.",
                "The hosting or preview environment may have its own infrastructure behaviour. This statement describes the Crownwing website code, not a guarantee that every browser, hosting platform, email provider or external site uses no cookies.",
            ]),
            ("fonts", "External fonts and technical requests", [
                "Our styles request fonts from fonts.googleapis.com and fonts.gstatic.com. Google states that the Google Fonts API does not set or log cookies. It does receive technical request information, including an IP address, requested URL and HTTP headers that can include browser and referrer information.",
                "No advertising-consent banner is displayed merely to suggest that the site uses tracking when it does not. The absence of cookies does not mean a font request is anonymous; the Privacy Policy explains the related information disclosure.",
            ]),
            ("forms-files", "Contact forms and browser caching", [
                "Submitting the contact form sends your entered details to Netlify Forms for Crownwing Parrots to review; the details are stored as a submission, not as a cookie in your browser. The website does not save form entries in local storage or session storage. Your browser’s own autofill and caching features are controlled by your browser settings.",
            ]),
            ("controls", "Your browser controls", [
                "You can inspect or remove cookies and website storage using your browser’s privacy settings. You can also clear autofill separately. Clearing browser data does not delete enquiries already submitted; contact us with a deletion request. Blocking external font requests may change the typeface shown but does not prevent you from reading the policy text.",
                "Following a link to another website, or sending an email through your chosen provider, takes you to services with their own privacy and cookie arrangements. Review their notices if you want to understand those services.",
            ]),
            ("future-changes", "If optional tracking is introduced", [
                "Any future non-essential cookies or similar tracking will need an updated notice and, where legally required, a way to give or refuse consent before that tracking starts. Such a feature is not included in the current website. Contact us if you have questions about what this site loads.",
            ]),
        ],
        "references": [
            ("https://developers.google.com/fonts/faq/privacy", "Google: how the Fonts API handles privacy"),
            ("/privacy-policy/", "Crownwing Parrots Privacy Policy"),
        ],
    },
    "/business-policies/": {
        "title": "Payments, Delivery, Cancellation & Refund Policy",
        "description": "Crownwing Parrots policies for bank-transfer payments, reservations, individual delivery arrangements, cancellations, returns, refunds and customer concerns.",
        "intro": "Read how enquiries, payments and agreed sales work, and which individual terms must be confirmed before you pay for a bird.",
        "sections": [
            ("business-sale", "Our business and the sales agreement", [
                "Crownwing Parrots is a sole-trader parrot breeder and retailer. This website supports enquiries; it does not have an online checkout or take payments through its forms. A submitted enquiry is not an order, payment or confirmed reservation.",
                "This policy should be read with the quotation, invoice, individual sales agreement and relevant species documentation. Individual terms must be clear before payment and supplied in a form the customer can keep. Nothing in this policy or an individual agreement excludes statutory rights that cannot lawfully be excluded.",
            ]),
            ("payments", "Payment methods and prices", [
                "Bank transfer is the confirmed payment method. Payment instructions will be provided with the relevant invoice or payment request. Card payments and other methods have not been confirmed and are not advertised as available.",
                "The price of the actual bird, applicable taxes and any agreed extra charges must be disclosed before payment is required. Where transport, documentation, veterinary work or another additional charge applies, its amount or basis must be explained in the quotation or agreement. A species photograph is not a priced offer for that individual bird.",
            ]),
            ("deposits", "Deposits and reservations", [
                "If a deposit is required, its amount, payment deadline, reservation period and treatment on cancellation must be stated in writing before you pay. There is no published standard deposit amount or blanket non-refundable deposit rule.",
                "Unless agreed otherwise in writing, a reservation is confirmed only after the required payment has been received and confirmed by Crownwing Parrots. Do not assume that preparing an enquiry reserves a bird. Any deposit term remains subject to applicable consumer law and must not remove a refund right provided by law.",
            ]),
            ("delivery-areas", "Collection and delivery availability", [
                "Collection, UK delivery or delivery to an international destination must be discussed for the specific bird and destination. No standard UK coverage area or international destination list has been confirmed. A city guide is not a promise of a branch, collection point or delivery route.",
                "A proposed handover depends on suitable welfare and transport arrangements, species restrictions, documentation, permits, veterinary requirements and any applicable import or export rules. Delivery may be declined where those requirements cannot be met. Do not travel to the contact address or arrange transport without agreeing the appointment and handover details first.",
            ]),
            ("delivery-costs-dates", "Delivery costs, dates and delays", [
                "There is no published flat delivery charge or guaranteed dispatch timeframe. The proposed destination, transport method and relevant additional costs must be confirmed before the customer commits to the arrangement. No additional charge should be imposed without prior disclosure and agreement where required.",
                "Estimated dates are agreed after the bird, documentation and transport arrangements have been confirmed. Weather, carrier availability, veterinary requirements and regulatory procedures can affect the plan. Significant delays should be communicated with an updated proposal; a delay does not remove any applicable statutory delivery or cancellation remedy.",
            ]),
            ("cancellation", "Cancellation before handover", [
                "To cancel, email either published business address with your name, bird description and order or invoice reference, if one has been issued. State clearly that you wish to cancel. You do not need to prepare a downloadable website enquiry to make that request.",
                "Cancellation and deposit treatment depend on the applicable law and the terms provided before the sale. Qualifying distance sales can carry a 14-day cancellation right, subject to the applicable rules and lawful exceptions. This website does not assert that every live-bird purchase is exempt, or that every purchase carries an unconditional change-of-mind return right.",
                "No standard voluntary cancellation fee or deposit-forfeiture rule has been decided. Any proposed fee or deposit condition must be explained before payment and must be lawful. An individual agreement cannot override mandatory consumer protections.",
            ]),
            ("returns", "Returns and safe arrangements", [
                "Contact Crownwing Parrots before attempting a return so that suitable care, documentation and transport can be coordinated. Do not post, ship or bring a bird to the business address without agreed safe arrangements. Do not delay necessary veterinary care while waiting for a response.",
                "There is no confirmed additional voluntary return window or flat return-transport charge. Any voluntary return arrangement must be agreed in writing. Where a legal right to return or another remedy applies, it takes precedence over discretionary terms; contacting us to coordinate welfare arrangements does not make a statutory right dependent on our approval.",
            ]),
            ("refunds", "Refunds", [
                "Refunds that are legally due must be made within the applicable statutory deadline. For qualifying distance-sale cancellations, the reimbursement rules can depend on receipt of returned goods or evidence of return. There is no separately confirmed standard Crownwing refund-processing timeframe.",
                "Unless another method is lawfully agreed or permitted, reimbursement uses the original payment method. A refund-processing fee will not be charged where the law prohibits it. Refund eligibility and timing must not be replaced by an unsupported blanket no-refunds statement.",
            ]),
            ("problems", "A wrong bird, a description issue or delivery concern", [
                "Tell us promptly if you believe the wrong bird was supplied, the bird does not match the agreed description, documentation is missing or another significant delivery or contractual concern has arisen. Provide the order or invoice reference, date of handover and a clear explanation. Relevant photographs, video or veterinary information may assist an assessment.",
                "Available remedies depend on the facts and applicable law. Crownwing Parrots will consider concerns in accordance with contractual and statutory rights, rather than treating every concern as a voluntary return. For an urgent health or welfare issue, contact an appropriate veterinary professional; website correspondence is not emergency veterinary care.",
            ]),
            ("changes", "Changes to a proposed order", [
                "Request changes to the selected bird, delivery address, date or other details as early as possible. A change is subject to availability, suitable transport and documentation. Any resulting price change or extra cost must be explained before the change is agreed; a customer request does not itself confirm a revised reservation.",
            ]),
            ("requirements", "Legal and welfare requirements", [
                "Sales and any transport must meet the animal-welfare, licensing, wildlife and import or export requirements applicable to the particular activity, species and destination. Where a permit, certificate or other document is required, it must be dealt with before the relevant handover.",
                "This policy is not a claim that Crownwing holds a particular licence, certification or international transport authorisation. Ask for the actual records relevant to your proposed purchase; do not infer approval from a general policy page or a species guide.",
            ]),
            ("individual-terms", "Terms that must be confirmed for the individual sale", [
                "Before paying, obtain the bird’s identity and price; accepted payment instructions; any deposit amount and refund conditions; the proposed collection or delivery location and costs; estimated dates; applicable cancellation rights; any additional voluntary return terms; and the refund arrangements. Keep the quotation and agreement for your records.",
                "These are transaction-specific terms, not hidden fixed conditions. The business has not yet set standard figures for deposits, delivery charges, cancellation fees, voluntary-return windows or refund-processing time. If a term remains unclear, ask for written clarification before proceeding.",
            ]),
            ("complaints-changes", "Complaints and policy updates", [
                "Send a complaint to info@crownwingparrots.co.uk or crownwingparrots@gmail.com with your contact details, relevant reference and the outcome you are seeking. Include supporting information where helpful, but do not send unnecessary sensitive documents. The business can use this information to investigate and respond.",
                "Policy changes should be clearly dated. They do not retrospectively replace the terms of an existing agreement or remove non-excludable consumer rights. General website information is not a substitute for the specific disclosures required before an individual sale.",
            ]),
        ],
        "references": [
            ("https://www.gov.uk/online-and-distance-selling-for-businesses", "GOV.UK: distance-selling information and cancellation rights"),
            ("https://www.gov.uk/accepting-returns-and-giving-refunds", "GOV.UK: returns and refunds"),
            ("/privacy-policy/", "How enquiry and customer information is handled"),
            ("/guides/buying-a-parrot-checklist/", "Questions to resolve before buying a parrot"),
        ],
    },
}