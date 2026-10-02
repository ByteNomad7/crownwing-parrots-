from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]/'dist'
count=0
for p in root.rglob('*.html'):
 s=p.read_text();old=s
 s=re.sub(r'<span class="(?:card-number|species-index)">.*?</span>','',s)
 s=s.replace('<span>01 / 08</span>','')
 s=re.sub(r'<div class="location-note">.*?</div>','',s,flags=re.S)
 s=re.sub(r'<p class="(?:gallery-note|contact-note|form-note)">.*?</p>','',s,flags=re.S)
 s=re.sub(r'<p class="group-note">.*?Examples include: (.*?)</p>',r'<p class="species-examples">Examples include: \1</p>',s,flags=re.S)
 s=s.replace('Representative species photo. ','')
 replacements={
 'It is not a live stock listing: current availability, individual details and prices need direct confirmation. ':'',
 'The representative photographs used in our collection explain the species; they do not identify a bird currently available to purchase. We do not label a bird as in stock without an actual listing.':'Explore the collection to learn about each group and prepare an enquiry about the birds that interest you.',
 'This website does not show live stock or publish unconfirmed prices. Representative photographs introduce species. Use the enquiry pages to request details about actual birds and proposed arrangements.':'Use the enquiry pages to request individual photographs, prices and proposed arrangements.',
 'Direct contact details will be added when supplied by the business. You can currently prepare and download an enquiry to keep ready for that conversation.':'Prepare and download an enquiry with the species and questions you would like to discuss.',
 'Direct email and telephone details will be added shortly. This form prepares a downloadable copy; it does not send your details or store them.':'Download a copy of your enquiry to keep your questions and preferences together.',
 'A location guide is not a claim of a local branch, local inventory or an established delivery service. Business premises and any service coverage will be added when confirmed. Choose your city below to explore the guide and prepare a downloadable enquiry.':'Choose your city below to explore the guide and prepare a downloadable enquiry.',
 'This page does not promise a local branch or a transport service.':'',
 'Do not assume a local branch, collection point or delivery route exists.':'',
 'This website does not publish unconfirmed price ranges.':'',
 'This creates a downloadable copy. It is not sent or stored.':'Download a copy of your enquiry for your records.',
 'It does not confirm a local branch or delivery service.':'',
 'Availability is confirmed directly. The photographs on this website represent species and are not live listings of individual birds.':'Ask about the individual birds available in your enquiry.',
 'No price is advertised here until those details are confirmed.':'',
 'No. Current birds and prices require direct confirmation. These pages help you research the care commitment and prepare a useful enquiry.':'Prepare an enquiry to request details and a quotation for an individual bird.',
 'Lifespan estimates differ between studies and species. Use this guide as a starting point and discuss the individual bird’s diet and care with an avian vet.':'',
 }
 for source,target in replacements.items():s=s.replace(source,target)
 s=re.sub(r'<p>\s*</p>','',s)
 if s!=old:p.write_text(s);count+=1
for name in ['app.js','common.js','local-enquiry.js']:
 p=root/name
 if p.exists():
  s=p.read_text().replace('Your enquiry copy is ready. It has not been sent.','Your enquiry copy is ready to download.').replace('Availability and arrangements need direct confirmation.\\n','')
  p.write_text(s)
print(f'Removed visible notices and repeated disclaimers across {count} pages.')
