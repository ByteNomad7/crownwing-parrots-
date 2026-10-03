"""Apply owner-approved topical consolidation without changing the design."""
import html
import json
import re
import shutil

from buyer_resources import refresh_extension, route_file, sections
from content_registry import ROOT
from route_rules import REDIRECTS, merged_target
from site_config import PUBLIC_ORIGIN

RECORDS = {
    "/guides/choosing-a-parrot/": [
        ("shared-home", "Agree responsibilities and usable space", """
<p>Check the same practical questions with every person who shares the home. Who supplies meals and water, cleans equipment, supervises activity and notices changes in appetite or behaviour? Who can take over if the usual keeper is delayed? Agreement should cover the ordinary routine, not just enthusiasm for a new companion.</p>
<p>Measure usable room with the planned enclosure, perches and household furniture in place. Identify where supervised movement can happen and how doors, windows and other animals will be managed. In shared accommodation, discuss vocalisation and any tenancy restrictions before choosing an individual. A compact bird still needs movement and social opportunities; limited room is not solved merely by buying the smallest cage.</p>"""),
        ("weekly-responsibilities", "Test a normal week and a difficult week", """
<ul><li><strong>Ordinary days:</strong> write down who provides familiar care, safe exercise and suitable interaction before and after work or study.</li>
<li><strong>Busy days:</strong> identify which responsibilities must still happen when plans change. A toy purchase is not a substitute for supervision and care.</li>
<li><strong>Time away:</strong> confirm a willing, capable backup keeper and whether the accommodation and familiar routine can remain suitable.</li>
<li><strong>Unexpected changes:</strong> decide who can contact the veterinary practice, arrange a journey or maintain care if the usual keeper is unavailable.</li></ul>
<p>Use this plan to compare needs, not to set a universal number of hours for every parrot. If the plan relies on unconfirmed help, mark it as unresolved. Put any additional care costs into the <a href="/guides/parrot-ownership-costs/">ownership budget</a>.</p>"""),
        ("first-time-expectations", "Check first-time expectations against the individual", """
<p>Write down what you expect from handling, vocalisation and companionship, then ask the current keeper what is actually known. Can the household accept a bird that does not talk, prefers limited touch or takes time to trust unfamiliar people? Labels such as young, hand-reared or tame do not answer those questions.</p>
<p>Separate a wish from a requirement the household cannot accommodate. Discuss the identified species and individual rather than choosing from photographs alone. Waiting is preferable to relying on a routine, space or temperament assumption that has not been resolved.</p>"""),
    ],
    "/guides/parrot-ownership-costs/": [
        ("backup-care-budget", "Budget for continuity of care", """
<p>Consider a week when you are away, unwell or unable to provide the ordinary routine. Identify a capable backup keeper, ask what care they can actually provide, and obtain any relevant provider quotation. Add planned paid care to your researched ownership estimates rather than assuming family help will always be available.</p>
<p>Keep clear instructions about familiar foods, secure accommodation, supervision and how to contact the veterinary practice. Confirm arrangements with the person concerned and revisit them when your circumstances change. Consider a future move, changed work pattern or loss of a regular carer, not only a short holiday. A continuity plan is a practical responsibility, not an advertised Crownwing boarding or transport service.</p>"""),
    ],
    "/guides/preparing-for-a-parrot/": [
        ("repeatable-exercise-route", "Make the safe exercise routine repeatable", """
<p>Before handover, identify the secure room, suitable perching opportunities and the person supervising activity. Walk through the doors, windows, fans, other animals and access to cooking or household hazards. Check the route again each time rather than assuming yesterday’s arrangement is still safe.</p>
<p>Agree how the bird can return to familiar accommodation without a rushed chase or forced interaction. Keep the initial routine predictable while learning its responses. Match equipment and movement opportunities to the exact species and individual; seek suitable help if safe supervision or return arrangements remain uncertain.</p>"""),
    ],
    "/guides/parrot-diet-nutrition/": [
        ("handover-feeding-record", "Keep a keeper-to-home feeding record", """
<p>Ask the current keeper to distinguish offered food from accepted food. Record the familiar products or ingredients, presentation, timing, how consumption is checked, and any established veterinary advice. Note information the keeper does not know rather than substituting a generic menu.</p>
<p>Keep this record with the handover information and use it when discussing a suitable feeding plan with an avian vet. Observe acceptance and appetite in the new routine. Household convenience is not a reason to make an abrupt diet change or assume different species have identical nutritional needs.</p>"""),
    ],
    "/guides/parrot-housing-enrichment/": [
        ("space-and-activity-plan", "Allocate usable space, activity and rest", """
<p>Assess accommodation with perches, bowls and activities installed, not from external cage dimensions alone. Check access for cleaning and inspection, secure fittings, and space for movement appropriate to the identified bird. Include replacement of worn or chewed equipment in the care budget.</p>
<p>Plan a manageable sequence of suitable foraging, chewing or climbing opportunities, supervised exercise and undisturbed rest. Observe which activities the bird uses and whether it can withdraw from attention. Inspect materials and wear, and revise the plan as you learn; a crowded enclosure or an ever-growing toy collection is not evidence of better enrichment.</p>"""),
    ],
    "/guides/buying-a-parrot-checklist/": [
        ("records-and-agreement", "Keep identity, terms and handover questions together", """
<p>Keep the written answers, current individual photographs and any relevant records together. Ask when photographs or video were taken; a brief clip cannot establish health, temperament or all-day behaviour. Distinguish recorded age and origin from estimates or gaps in history. Ask which identification and documentation relate to the actual bird, using the scientific name where official checks require it.</p>
<p>Before travelling or paying, confirm the quoted individual, included items, written terms, handover location and responsibility for any proposed journey. Use the <a href="/guides/cites-parrots-uk/">documentation guide</a> to separate transaction and movement questions. Unresolved information should remain visible in your notes; no single photograph, ring or generic assurance proves every legal or health requirement.</p>"""),
    ],
    "/guides/": [
        ("decision-led-discovery", "Choose a resource by the decision you need to make", """
<p>Household planning is useful wherever you live. Follow the guide for <a href="/guides/choosing-a-parrot/">species choice</a>, <a href="/guides/preparing-for-a-parrot/">home preparation</a>, <a href="/guides/parrot-ownership-costs/">care costs</a> or <a href="/guides/buying-a-parrot-checklist/">seller questions</a> rather than treating a city name as evidence of local stock or premises.</p>
<p>Northern Ireland movement questions have a distinct official framework: use the <a href="/locations/belfast/">Belfast and Northern Ireland planning aid</a> alongside the documentation guide. Include your actual location and proposed arrangements in the <a href="/contact/">contact enquiry form</a>.</p>"""),
    ],
}


def rewrite_links(text):
    def href(match):
        path = match[2]
        absolute = path.startswith(PUBLIC_ORIGIN + "/")
        local = path.removeprefix(PUBLIC_ORIGIN) if absolute else path
        route, _, query = local.partition("?")
        route, _, fragment = route.partition("#")
        target = merged_target(route)
        if target is None:
            return match[0]
        # City-form fragments cannot survive retirement; shared contact is the
        # appropriate path for form access, without copying stale anchor IDs.
        if fragment:
            target = "/contact/"
        value = (PUBLIC_ORIGIN if absolute else "") + target + ("?" + query if query else "")
        return match[1] + html.escape(value, quote=True) + match[3]
    text = re.sub(r'(\bhref=")([^"]+)(")', href, text)
    text = text.replace("UK city guides", "UK buying guides")
    text = text.replace("Our city guides help buyers plan from their area; they do not identify Crownwing branches or local stock.",
                        "Our buyer guides help you prepare; they do not identify Crownwing branches or local stock.")
    def schema(match):
        data = json.loads(match[2])
        def visit(value):
            if isinstance(value, dict):
                for key, item in list(value.items()):
                    if isinstance(item, str) and item in {PUBLIC_ORIGIN + r for r in REDIRECTS}:
                        value[key] = PUBLIC_ORIGIN + REDIRECTS[item.removeprefix(PUBLIC_ORIGIN)]
                        if key == "item" and "name" in value:
                            value["name"] = "Parrot guides"
                    else:
                        visit(item)
            elif isinstance(value, list):
                for child in value:
                    visit(child)
        visit(data)
        return match[1] + json.dumps(data, ensure_ascii=False).replace("</", "<\\/") + match[3]
    return re.sub(r'(<script type="application/ld\+json"[^>]*>)(.*?)(</script>)', schema, text, flags=re.S)


def apply_city_consolidation():
    for path, records in RECORDS.items():
        target = route_file(path)
        block = '<div id="approved-city-consolidation">' + sections(records) + "</div>"
        target.write_text(refresh_extension(target.read_text(), block, "approved-city-consolidation"))
    for source in REDIRECTS:
        target = route_file(source)
        if target.exists():
            archive = ROOT / "seo/retired-city-pages" / (source.strip("/").replace("/", "-") + ".html")
            archive.parent.mkdir(parents=True, exist_ok=True)
            if not archive.exists():
                shutil.copyfile(target, archive)
            target.unlink()
            if not any(target.parent.iterdir()):
                target.parent.rmdir()
    for target in (ROOT / "dist").rglob("index.html"):
        target.write_text(rewrite_links(target.read_text()))