/* ============================================================
   IFILAF — progressive enhancements only.
   The app fully works without this file: filters, search, menu
   open/close, the Found-only field and validation messages all
   render from the server or pure CSS. What's left here:

   1. Account menu: outside-click / Escape dismissal (<details>
      already handles open/close and keyboard).
   2. Photo previews + per-photo removal on the item form.
   3. Inline validation of the two required fields, mirroring
      the server's messages; server re-renders them when JS is off.
   4. Search clear button.
   5. Delete confirmation.
   6. Item gallery: a thumbnail selects the big photo.
   ============================================================ */
(function () {
  'use strict';

  /* 1 — account menu: dismiss on outside click / Escape ---------- */
  var userMenu = document.querySelector('.nav__user');
  if (userMenu) {
    document.addEventListener('click', function (e) {
      if (userMenu.open && !userMenu.contains(e.target)) userMenu.open = false;
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && userMenu.open) {
        userMenu.open = false;
        userMenu.querySelector('summary').focus();
      }
    });
  }

  /* 2 — photo previews on the item form (multiple photos) -------- */
  var form = document.querySelector('[data-item-form]');
  if (form) {
    var file = form.querySelector('#in-photo');
    var list = form.querySelector('#photoList');
    var saved = form.querySelector('#photoPrev');
    var savedX = saved && saved.querySelector('[data-remove-photo]');
    var xIcon = savedX ? savedX.innerHTML : '×';
    var blobs = [];

    function picked() {
      return file.files ? Array.prototype.slice.call(file.files) : [];
    }

    // One thumbnail per picked file, each with its own remove button.
    function paint() {
      blobs.forEach(function (u) { URL.revokeObjectURL(u); });   // don't leak blob URLs
      blobs = [];
      list.textContent = '';

      picked().forEach(function (f, i) {
        var url = URL.createObjectURL(f);
        blobs.push(url);

        var thumb = document.createElement('div');
        thumb.className = 'photo__prev';

        var img = document.createElement('img');
        img.src = url;
        img.alt = '';

        var x = document.createElement('button');
        x.type = 'button';
        x.className = 'photo__x';
        x.setAttribute('aria-label', 'Remove photo ' + (i + 1));
        x.innerHTML = xIcon;
        x.addEventListener('click', function () { drop(i); });

        thumb.appendChild(img);
        thumb.appendChild(x);
        list.appendChild(thumb);
      });
    }

    // Rebuild the picker's files without the removed one. Where
    // DataTransfer is unavailable the picker is cleared instead.
    function drop(index) {
      var rest = picked();
      rest.splice(index, 1);
      try {
        var dt = new DataTransfer();
        rest.forEach(function (f) { dt.items.add(f); });
        file.files = dt.files;
      } catch (err) {
        file.value = '';
      }
      paint();
      file.focus();
    }

    file.addEventListener('change', paint);

    if (savedX) savedX.addEventListener('click', function () {
      saved.hidden = true;
      saved.querySelector('img').removeAttribute('src');
      file.focus();
    });

    /* 3 — inline validation of name + location ------------------- */
    var MSGS = {
      name: 'Give the item a name.',
      location: 'Add where it was lost or found.'
    };

    function setError(key, msg) {
      var field = form.querySelector('#f-' + key);
      var out = form.querySelector('#e-' + key);
      var input = form.querySelector('#in-' + key);
      field.classList.toggle('is-error', !!msg);
      out.textContent = msg || '';
      out.hidden = !msg;
      input.setAttribute('aria-invalid', msg ? 'true' : 'false');
    }

    // Clear an error the moment the field becomes valid again.
    ['name', 'location'].forEach(function (key) {
      form.querySelector('#in-' + key).addEventListener('input', function (e) {
        if (e.target.value.trim()) setError(key, '');
      });
    });

    form.addEventListener('submit', function (e) {
      var firstBad = null;
      ['name', 'location'].forEach(function (key) {
        var input = form.querySelector('#in-' + key);
        if (!input.value.trim()) {
          setError(key, MSGS[key]);
          firstBad = firstBad || input;
        } else {
          setError(key, '');
        }
      });
      if (firstBad) { e.preventDefault(); firstBad.focus(); }
    });
  }

  /* 4 — search clear button -------------------------------------- */
  document.querySelectorAll('.search').forEach(function (search) {
    var input = search.querySelector('input[type="search"]');
    var clear = search.querySelector('[data-clear-search]');
    if (!input) return;

    var submitTimeout;
    input.addEventListener('input', function () {
      window.clearTimeout(submitTimeout);
      submitTimeout = window.setTimeout(function () {
        search.submit();
      }, 600);
    });

    search.addEventListener('submit', function () {
      window.clearTimeout(submitTimeout);
    });

    if (clear) clear.addEventListener('click', function (e) {
      e.preventDefault();
      window.clearTimeout(submitTimeout);
      input.value = '';
      search.submit();
    });
  });

  /* 6 — item gallery: thumbnail selects the big photo ------------ */
  document.querySelectorAll('[data-gallery]').forEach(function (gallery) {
    var main = gallery.querySelector('.gallery__main');
    var thumbs = gallery.querySelectorAll('[data-gallery-thumb]');
    if (!main || thumbs.length < 2) return;

    thumbs.forEach(function (thumb) {
      thumb.addEventListener('click', function () {
        main.src = thumb.dataset.src;
        thumbs.forEach(function (t) {
          t.classList.toggle('is-active', t === thumb);
          if (t === thumb) t.setAttribute('aria-current', 'true');
          else t.removeAttribute('aria-current');
        });
      });
    });
  });

  /* 5 — account management delete confirmation ------------------- */
  document.querySelectorAll('a.account-list-item__delete[data-confirm]').forEach(function (link) {
    link.addEventListener('click', function (e) {
      if (!window.confirm(link.dataset.confirm)) e.preventDefault();
    });
  });
})();