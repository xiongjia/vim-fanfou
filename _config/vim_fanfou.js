/* vim_fanfou.js */
(function () {
  'use strict';
  $(document).ready(function() {

    /* right bar */
    function showRightBar() {
      var toc, tocToggler;

      /* create the TOC Menu */
      tocToggler = $('<div class="vw-tocHdr"/>' +
        '<div class="toggler" title="TOC">Table of contents</div>');
      toc = $('.toc');
      toc.wrap('<div class="vw-right">');
      $('.vw-right').prepend(tocToggler)
        .delay(100)
        .fadeTo(500, '0.5')
        .hover(function() {
          $(this).stop().fadeTo(300, '0.9');
        }, function() {
          $(this).stop().fadeTo(300, '0.5');
        });
      $('div.toc').slideToggle(300);
      tocToggler.click(function() {
          $('div.toc').slideToggle(300);
        });
    }
 
    /* update external links */
    $('a[href]').each(function() {
      if (this.href.indexOf(window.location.host) === -1) {
        $(this).attr({ target: '_blank', title: this.href });
      }
    });

    /* image lazy load */
    $('img.lazy').lazyload();
    if (window.innerWidth >= 450) {
      /* show right bar */
      showRightBar();
    }
  });
})();

