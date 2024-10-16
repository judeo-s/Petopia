document.addEventListener('DOMContentLoaded', () => {
  const navLinks = document.querySelectorAll('nav ul li a');
  const menuToggle = document.getElementById('menu-toggle');
  const navUl = document.getElementById('nav-links');

  navLinks.forEach((link) => {
    link.addEventListener('click', smoothScroll);
  });

  menuToggle.addEventListener('click', () => {
    navUl.classList.toggle('show');
  });

  const lazyImages = document.querySelectorAll("img[loading='lazy']");
  lazyImages.forEach((img) => {
    img.addEventListener('load', () => {
      img.classList.add('loaded');
    });
  });

  const projectRepoButton = document.querySelector('.project-repo');
  projectRepoButton.addEventListener('click', () => {
    window.location.href = 'https://github.com/judeo-s/Petopia.git';
  });
});

function smoothScroll(event) {
  event.preventDefault();
  const targetId = event.currentTarget.getAttribute('href').substring(1);
  const targetSection = document.getElementById(targetId);

  window.scrollTo({
    top:
      targetSection.offsetTop - document.querySelector('header').offsetHeight,
    behavior: 'smooth',
  });
}
