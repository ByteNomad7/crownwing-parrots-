const menu = document.querySelector('.menu');
const nav = document.querySelector('nav');

if (menu && nav) {
  menu.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    menu.setAttribute('aria-expanded', String(open));
    menu.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
  });
}

const dialog = document.getElementById('photo-dialog');
const gallery = document.querySelector('.detail-gallery');

if (dialog && gallery) {
  const buttons = [...gallery.querySelectorAll('[data-photo-src]')];
  const photos = buttons.map(button => ({
    src: button.dataset.photoSrc,
    alt: button.dataset.photoAlt,
    width: button.dataset.photoWidth,
    height: button.dataset.photoHeight,
  }));
  const enlarged = dialog.querySelector('img');
  const caption = dialog.querySelector('.photo-dialog-caption');
  const previous = dialog.querySelector('.photo-prev');
  const next = dialog.querySelector('.photo-next');
  const mainImage = gallery.querySelector('.gallery-main img');
  const mainCaption = gallery.querySelector('.gallery-caption');
  let current = 0;

  function showPhoto(index) {
    current = (index + photos.length) % photos.length;
    const photo = photos[current];
    // The image optimiser adds srcset to the initial photo. These dynamic
    // images must use the selected src, not that first-photo candidate list.
    for (const image of [enlarged, mainImage]) {
      image.removeAttribute('srcset');
      image.removeAttribute('sizes');
    }
    enlarged.src = photo.src;
    enlarged.alt = photo.alt;
    enlarged.width = Number(photo.width);
    enlarged.height = Number(photo.height);
    caption.textContent = `${photo.alt} · Photo ${current + 1} of ${photos.length}`;
    previous.disabled = next.disabled = photos.length < 2;
    mainImage.src = photo.src;
    mainImage.alt = photo.alt;
    mainImage.width = Number(photo.width);
    mainImage.height = Number(photo.height);
    gallery.querySelector('.gallery-main').setAttribute('aria-label', `Enlarge ${photo.alt}`);
    mainCaption.firstChild.textContent = photo.alt;
  }

  buttons.forEach((button, index) => {
    button.addEventListener('click', () => {
      const selected = button.classList.contains('gallery-main') ? current : index;
      showPhoto(selected);
      if (!dialog.open) dialog.showModal();
    });
  });

  previous.addEventListener('click', () => showPhoto(current - 1));
  next.addEventListener('click', () => showPhoto(current + 1));
  dialog.querySelector('.close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    if (event.target === dialog) dialog.close();
  });
  dialog.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft') {
      event.preventDefault();
      showPhoto(current - 1);
    } else if (event.key === 'ArrowRight') {
      event.preventDefault();
      showPhoto(current + 1);
    }
  });
}
