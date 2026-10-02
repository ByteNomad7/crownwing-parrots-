"""Server-rendered markup for Crownwing's buyer planning tools."""

from html import escape


GROUPS = [
    {
        "id": "macaws",
        "name": "Macaws",
        "facets": [
            "Mini macaws and large macaws differ greatly in adult scale, activity and strength.",
            "Large macaw calls can carry a long way; smaller size does not promise silence.",
            "Some may speak or mimic sounds; spoken words are never assured.",
            "Plan for social contact alongside independent activity and food-search opportunities.",
            "A broad planning horizon is roughly 25–50 years or more; species and individuals differ.",
            "Large macaws need substantial, sturdy accommodation; mini macaws also need room to climb, flap and play.",
            "First-time owners should weigh size, noise, strength and long-term demands carefully.",
            "Plan time for cleaning, interaction, exercise and care during holidays or illness.",
            "Rotate safe toys and foraging opportunities; provide varied physical challenges.",
            "Families need adult-led supervision, agreed boundaries and a protected space away from busy traffic.",
        ],
    },
    {
        "id": "cockatoos",
        "name": "Cockatoos",
        "facets": [
            "Commonly kept cockatoos differ in scale; a cockatiel is much smaller than larger cockatoos.",
            "Many have forceful calls; vocal patterns differ by species and individual.",
            "Some may imitate sounds or words, but talking is variable and not assured.",
            "Strong interest in company can sit alongside a need for calm independent activity.",
            "A broad planning range is about 25–60 years, with marked species differences.",
            "Provide sturdy housing, room to climb and stretch, and supervised exercise in a bird-safe area.",
            "First-time owners should consider loud calls, daily interaction and the bird's emotional needs.",
            "Allow time for interaction, rest, foraging, regular cleaning and replaceable safe materials.",
            "Alternate shared interaction with food puzzles, safe destruction and quiet independent time.",
            "Adults should lead care and supervise children; provide an undisturbed refuge.",
        ],
    },
    {
        "id": "amazons",
        "name": "Amazons",
        "facets": [
            "Many commonly kept Amazons are around 30–38 cm in adult total length; species differ.",
            "Some Amazons are notably vocal; calls can be loud at predictable busy times.",
            "Some mimic words, whistles or household sounds; others may speak little or not at all.",
            "Provide daily interaction while building foraging and independent play into the schedule.",
            "A broad planning horizon is roughly 30–50 years or longer, depending on species and individual.",
            "A secure enclosure, robust perches and space to climb and exercise are still essential.",
            "First-time owners should be willing to learn parrot communication and manage confident behaviour.",
            "Plan a steady daily routine, recurring care and future arrangements if circumstances change.",
            "Use foraging and independent play, alongside gradual positive-reinforcement training.",
            "An adult should be responsible for routines; families should supervise children and keep a calm retreat.",
        ],
    },
    {
        "id": "eclectus",
        "name": "Eclectus",
        "facets": [
            "Adult total length is generally about 35–42 cm, varying among Eclectus species and individuals.",
            "Eclectus can make loud calls; daily vocal patterns depend on the individual and surroundings.",
            "Some may mimic sounds or words, but neither speech nor a particular noise level is promised.",
            "Offer regular social contact while helping the bird spend some time independently.",
            "A broad planning range of roughly 25–40 years is reasonable; individual outcomes vary.",
            "Provide a climbing enclosure, varied perches and supervised exercise outside it.",
            "First-time owners need willingness to learn daily nutrition, body language and routine.",
            "Plan for ongoing enrichment, suitable care, noise, travel cover and a possible multi-decade commitment.",
            "Rotate safe chew and food-search activities; provide supervised exercise and foraging.",
            "Adults should lead care and supervise children; offer a quiet retreat and gradual introductions.",
        ],
    },
    {
        "id": "conures",
        "name": "Conures",
        "facets": [
            "Many popular conure species measure around 25–40 cm from bill to tail; species differ.",
            "Sun conures may make piercing calls; smaller size does not mean a quiet home.",
            "Some birds imitate sounds, but speech is not assured.",
            "Create a rhythm of interaction, independent play and quiet rest; preferences vary.",
            "A roughly 20–35-year planning range is often cited; species and individuals vary.",
            "Secure housing and room to climb, stretch and move matter even for smaller conures.",
            "First-time owners should prepare for vocal calls and daily social needs.",
            "Plan time for daily social contact, exercise, cleaning and care during travel.",
            "Food puzzles, safe climbing and supervised exploration offer activity and choice.",
            "Families need an adult to lead care and supervise children; keep other pets safely apart.",
        ],
    },
    {
        "id": "caiques",
        "name": "Caiques",
        "facets": [
            "Black-headed and white-bellied caiques are typically about 23–25 cm; individuals vary.",
            "Caiques can be vocally lively; intensity and frequency are individual.",
            "No talking outcome can be promised for an individual caique.",
            "Balance activity shared with people and independent ways to investigate.",
            "A broad species-dependent planning horizon is roughly 25–40 years; no lifespan is guaranteed.",
            "Compact dimensions still call for secure housing and supervised space to move.",
            "Their curiosity and energy call for active supervision, structure and boundaries.",
            "Plan for supervised daily activity, predictable down time and long-term care.",
            "Rotate play objects; use food searches, safe textures and short training sessions.",
            "If other birds live in the home, plan separate resources and careful introductions.",
        ],
    },
    {
        "id": "african-parrots",
        "name": "African Grey Parrots",
        "facets": [
            "Congo African greys are generally larger than Timneh parrots; confirm the exact type.",
            "Calls can be sharp or persistent; consider how sound carries through your home.",
            "Some imitate sounds and may develop spoken words; vocabulary and frequency cannot be promised.",
            "Provide social contact alongside food-search games, destructible materials and quiet periods.",
            "A broad 30–50-year planning range is used for African Grey Parrots; estimates vary.",
            "Provide a secure, roomy enclosure, varied perches and supervised movement in a parrot-safe area.",
            "First-time owners should be ready to learn body language and establish a consistent routine.",
            "Plan daily interaction, cleaning, enrichment, future care and potentially decades of commitment.",
            "Rotate safe chewing, shredding and foraging activities; allow mental work every day.",
            "Adults should supervise children; agree household responsibilities and provide a quiet retreat.",
        ],
    },
    {
        "id": "parakeets-small-psittacines",
        "name": "Parakeets & small psittacines",
        "facets": [
            "The group spans tiny parrotlets to larger ringnecks; exact species changes adult size.",
            "Budgies may chatter frequently; ringnecks can have a much louder, carrying call.",
            "Some may talk, but no bird is guaranteed to mimic words.",
            "Many are social and active; preferences differ and human contact may not replace bird companionship.",
            "There is no single group lifespan estimate; budgerigars, ringnecks and lovebirds differ.",
            "Match flight space, bar spacing and perch diameter to the exact species.",
            "Small dimensions do not make a bird a display animal or remove daily care needs.",
            "Allow for daily care, suitable social plans, travel cover and long-term species-specific planning.",
            "Provide foraging, shredding, climbing, supervised exercise and varied safe textures.",
            "Families should supervise children; adults remain responsible for feeding, cleaning and handling.",
        ],
    },
]

FACETS = [
    ("size", "Size"),
    ("noise", "Noise"),
    ("talkingability", "Talking ability"),
    ("socialneeds", "Social needs"),
    ("lifespan", "Lifespan"),
    ("space", "Space"),
    ("experience", "Experience"),
    ("time", "Time"),
    ("enrichment", "Enrichment"),
    ("householdfit", "Household fit"),
]


def render_comparison():
    """Return a complete, readable comparison table with no JavaScript dependency."""
    headings = "".join(
        f'<th scope="col" data-group="{escape(group["id"])}">{escape(group["name"])}</th>'
        for group in GROUPS
    )
    rows = []
    for index, (facet_id, facet_name) in enumerate(FACETS):
        cells = "".join(
            f'<td data-group="{escape(group["id"])}">{escape(group["facets"][index])}</td>'
            for group in GROUPS
        )
        rows.append(
            f'<tr><th scope="row" data-facet="{escape(facet_id)}">{escape(facet_name)}</th>{cells}</tr>'
        )
    options = "".join(
        f'<option value="{escape(group["id"])}">{escape(group["name"])}</option>'
        for group in GROUPS
    )
    return f"""<section class="buyer-tool buyer-comparison" id="group-comparison" aria-labelledby="comparison-title">
  <div class="buyer-tool__intro">
    <p class="eyebrow">A considered shortlist</p>
    <h2 id="comparison-title">Compare the day-to-day, not a score</h2>
    <p>Use this guide to start a conversation about the exact species and individual. Group descriptions are broad context, not a prediction of any one bird.</p>
  </div>
  <div class="comparison-controls" hidden>
    <label for="comparison-first">First group
      <select id="comparison-first" name="comparison-first"><option value="">Choose a group</option>{options}</select>
    </label>
    <label for="comparison-second">Second group
      <select id="comparison-second" name="comparison-second"><option value="">Choose a group</option>{options}</select>
    </label>
    <button class="button" type="button" data-comparison-show>Show comparison</button>
    <button class="button lime" type="button" data-comparison-reset>Reset — show all</button>
    <p class="buyer-tool__message" data-comparison-message role="status" aria-live="polite"></p>
  </div>
  <p class="buyer-tool__caveat">There is variation between species and individual birds within every group. Talking is never guaranteed. No group is ranked here, and this comparison does not indicate current availability.</p>
  <div class="comparison-table-wrap" tabindex="0" role="region" aria-label="Parrot group comparison table; scroll horizontally to read all columns">
    <table class="comparison-table">
      <caption>Broad care considerations by parrot group</caption>
      <thead><tr><th scope="col">Consideration</th>{headings}</tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
  </div>
  <noscript><p class="buyer-tool__note">The full comparison is shown above. Group selection is an optional convenience when JavaScript is available.</p></noscript>
</section>"""


def render_budget():
    """Return a local-only ownership budget calculator form and result region."""
    fields = [
        ("purchase", "Purchase", "one-off", True),
        ("cage", "Cage / accommodation", "one-off", True),
        ("initialEquipment", "Initial equipment", "one-off", True),
        ("transport", "Transport", "one-off", True),
        ("food", "Food", "monthly", True),
        ("toys", "Toys and enrichment", "monthly", True),
        ("veterinarySaving", "Veterinary saving", "monthly", True),
        ("insurance", "Insurance", "monthly", False),
        ("emergencyReserve", "Emergency reserve", "ring-fenced one-off", True),
    ]
    field_markup = []
    for field_id, label, cadence, required in fields:
        required_attr = " required" if required else ""
        optional = "" if required else '<span class="buyer-tool__optional">Optional — enter £0 if not budgeting for insurance.</span>'
        default_value = ' value="0"' if field_id == "insurance" else ""
        field_markup.append(
            f"""<label class="budget-field" for="budget-{field_id}">
  <span class="budget-field__name">{escape(label)}{optional}</span>
  <span class="budget-field__input"><span aria-hidden="true">£</span><input id="budget-{field_id}" name="{escape(field_id)}" type="number" inputmode="decimal" min="0" step="0.01"{required_attr}{default_value} aria-describedby="budget-{field_id}-hint"><span class="budget-field__cadence" id="budget-{field_id}-hint">{escape(cadence)}</span></span>
</label>"""
        )
    return f"""<section class="buyer-tool buyer-budget" id="ownership-budget" aria-labelledby="budget-title">
  <div class="buyer-tool__intro">
    <p class="eyebrow">Plan for the whole commitment</p>
    <h2 id="budget-title">Build your own ownership budget</h2>
    <p>Enter your own estimates for the bird and care plan you have in mind. This is a planning aid, not a retailer quote.</p>
  </div>
  <form class="budget-form" data-budget-form autocomplete="off" novalidate>
    <p class="budget-form__instruction">Amounts are in pounds sterling. Enter a value for each required item; £0 is valid when it reflects your plan. Monthly amounts are treated as monthly estimates.</p>
    <div class="budget-fields">{''.join(field_markup)}</div>
    <p class="buyer-tool__note">The emergency reserve is shown as ring-fenced starting cash; it is not counted as planned spending. Nothing you enter is sent or stored: calculation happens locally in this browser.</p>
    <div class="budget-actions">
      <button class="button" type="submit" disabled>Calculate my budget</button>
      <button class="button lime" type="reset">Reset</button>
    </div>
    <p class="buyer-tool__error" data-budget-error role="alert" aria-live="assertive"></p>
    <noscript><p class="buyer-tool__note">Calculation requires JavaScript. The budget categories remain readable, but submission is disabled so your estimates are not sent as a page request.</p></noscript>
  </form>
  <section class="budget-results" data-budget-results aria-labelledby="budget-results-title" aria-live="polite" hidden>
    <p class="eyebrow">Your estimate</p>
    <h3 id="budget-results-title">A clearer starting point</h3>
    <dl class="budget-results__list">
      <div><dt>Setup spend</dt><dd data-result="setupSpend">—</dd></div>
      <div><dt>Monthly ongoing estimate</dt><dd data-result="monthlyOngoing">—</dd></div>
      <div><dt>First-year planned spend <span>excluding emergency reserve</span></dt><dd data-result="firstYearPlannedSpend">—</dd></div>
      <div><dt>Starting cash <span>including ring-fenced reserve</span></dt><dd data-result="startingCash">—</dd></div>
      <div class="budget-results__reserve"><dt>Emergency reserve <span>kept separate; not counted as spent</span></dt><dd data-result="emergencyReserve">—</dd></div>
    </dl>
    <p class="buyer-tool__note">These totals use only the estimates you entered. They are not Crownwing prices or a guarantee of future costs.</p>
  </section>
</section>"""