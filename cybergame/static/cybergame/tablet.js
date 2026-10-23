/* Cyber Squad: the pretend tablet.
 *
 * Draws a whole tablet from the round in #tablet-data: a lock screen, a home
 * screen of apps, and working Messages, Phone, Contacts, Mail, Web and a
 * game (Pixel Park), plus Photos, Camera, Music and Settings so it feels
 * real. Nothing is typed: every message is a ready-made choice.
 *
 * Every tap that matters carries an action key. act(key):
 *   - a key in setup.partials is remembered and the round goes on
 *   - any other key the round scores ends the round right there
 *   - anything else is just the tablet working like a tablet
 * "I'm finished" posts "done" plus everything remembered; the server scores
 * it (see views._tablet_choice), so the stars are decided there, not here.
 *
 * Sounds are made on the spot with the Web Audio API: no sound files, no
 * downloads, nothing sent to anyone. Voices on calls use the browser's own
 * speech, the same as the read-aloud button elsewhere in the game.
 */
(function () {
  "use strict";

  var DATA = JSON.parse(document.getElementById("tablet-data").textContent);
  var root = document.getElementById("tablet");
  var form = document.getElementById("tab-form");
  var hintEl = document.getElementById("tab-hint");
  var finishBtn = document.getElementById("tab-finish");
  var soundBtn = document.getElementById("tab-sound");
  var tipsBtn = document.getElementById("tab-tips");

  var OUT = DATA.outcomes || {};
  var PARTIALS = DATA.partials || [];
  var CALLS = DATA.calls || {};
  var HINTS = !!DATA.hints;

  // ---------------------------------------------------------------- helpers

  function store(key, value) {
    try {
      if (value === undefined) return window.localStorage.getItem(key);
      window.localStorage.setItem(key, value);
    } catch (e) { /* private window, blocked storage: just don't remember */ }
    return null;
  }

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function clone(o) { return JSON.parse(JSON.stringify(o == null ? null : o)); }

  function digits(s) {
    var d = String(s || "").replace(/\D/g, "");
    return d.length > 10 ? d.slice(-10) : d;
  }

  function initials(name) {
    var words = String(name).replace(/[^A-Za-z ]/g, "").split(" ").filter(Boolean);
    return (words.length > 1 ? words[0][0] + words[1][0] : (words[0] || "?")[0]).toUpperCase();
  }

  function later(fn, ms) { return setTimeout(fn, ms); }

  // ----------------------------------------------------------------- sounds

  var Sound = (function () {
    var ctx = null, master = null, alarm = null;
    var muted = store("cs-muted") === "1";

    function ac() {
      if (!ctx) {
        var C = window.AudioContext || window.webkitAudioContext;
        if (!C) return null;
        try {
          ctx = new C();
          master = ctx.createGain();
          master.gain.value = muted ? 0 : 0.5;
          master.connect(ctx.destination);
        } catch (e) { ctx = null; return null; }
      }
      if (ctx.state === "suspended") { try { ctx.resume(); } catch (e) { /* ignore */ } }
      return ctx;
    }

    function tone(f, at, dur, type, vol, slideTo) {
      var c = ac(); if (!c) return;
      var t = c.currentTime + at, o = c.createOscillator(), g = c.createGain();
      o.type = type || "sine";
      o.frequency.setValueAtTime(f, t);
      if (slideTo) o.frequency.exponentialRampToValueAtTime(slideTo, t + dur);
      g.gain.setValueAtTime(0.0001, t);
      g.gain.exponentialRampToValueAtTime(vol || 0.3, t + 0.012);
      g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
      o.connect(g); g.connect(master);
      o.start(t); o.stop(t + dur + 0.03);
    }

    function hiss(at, dur, vol, from, to) {
      var c = ac(); if (!c) return;
      var n = Math.max(1, Math.floor(c.sampleRate * dur));
      var buf = c.createBuffer(1, n, c.sampleRate), d = buf.getChannelData(0);
      for (var i = 0; i < n; i++) d[i] = Math.random() * 2 - 1;
      var src = c.createBufferSource(), bp = c.createBiquadFilter(), g = c.createGain();
      var t = c.currentTime + at;
      src.buffer = buf; bp.type = "bandpass"; bp.Q.value = 1.1;
      bp.frequency.setValueAtTime(from, t);
      bp.frequency.exponentialRampToValueAtTime(to, t + dur);
      g.gain.setValueAtTime(0.0001, t);
      g.gain.exponentialRampToValueAtTime(vol, t + dur * 0.25);
      g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
      src.connect(bp); bp.connect(g); g.connect(master);
      src.start(t); src.stop(t + dur);
    }

    var DTMF = { "1": [697, 1209], "2": [697, 1336], "3": [697, 1477], "4": [770, 1209],
      "5": [770, 1336], "6": [770, 1477], "7": [852, 1209], "8": [852, 1336],
      "9": [852, 1477], "*": [941, 1209], "0": [941, 1336], "#": [941, 1477] };

    return {
      wake: ac,
      isMuted: function () { return muted; },
      setMuted: function (m) {
        muted = m;
        store("cs-muted", m ? "1" : "0");
        if (master) master.gain.value = m ? 0 : 0.5;
        if (m) hush();
      },
      tap: function () { hiss(0, 0.03, 0.12, 3200, 2200); },
      unlock: function () { tone(1320, 0, 0.06, "sine", 0.12); tone(1760, 0.05, 0.08, "sine", 0.1); },
      text: function () { tone(1175, 0, 0.12, "sine", 0.32); tone(1568, 0.11, 0.16, "sine", 0.32); tone(1397, 0.25, 0.22, "sine", 0.28); },
      mail: function () { hiss(0, 0.4, 0.32, 500, 4200); tone(880, 0.3, 0.2, "sine", 0.16); },
      game: function () { tone(660, 0, 0.08, "square", 0.1); tone(990, 0.09, 0.14, "square", 0.1); },
      sent: function () { hiss(0, 0.24, 0.22, 700, 5200); },
      ring: function () { tone(440, 0, 1.0, "sine", 0.1); tone(480, 0, 1.0, "sine", 0.1); },
      busy: function () {
        for (var i = 0; i < 3; i++) { tone(480, i * 0.5, 0.25, "sine", 0.1); tone(620, i * 0.5, 0.25, "sine", 0.1); }
      },
      key: function (k) {
        var p = DTMF[k]; if (!p) return;
        tone(p[0], 0, 0.14, "sine", 0.13); tone(p[1], 0, 0.14, "sine", 0.13);
      },
      shutter: function () { hiss(0, 0.07, 0.4, 2400, 900); hiss(0.08, 0.06, 0.3, 1600, 700); },
      alarmOn: function () {
        if (alarm) return;
        var beep = function () {
          for (var i = 0; i < 4; i++) tone(i % 2 ? 740 : 988, i * 0.17, 0.13, "square", 0.07);
        };
        beep();
        alarm = setInterval(beep, 1600);
      },
      alarmOff: function () { clearInterval(alarm); alarm = null; },
      win: function () { [523, 659, 784, 1047].forEach(function (f, i) { tone(f, i * 0.09, 0.28, "triangle", 0.28); }); },
      meh: function () { tone(659, 0, 0.18, "triangle", 0.24); tone(784, 0.15, 0.26, "triangle", 0.24); },
      lose: function () { tone(330, 0, 0.3, "sawtooth", 0.1, 220); tone(247, 0.28, 0.45, "sawtooth", 0.1, 150); }
    };
  })();

  var VOICE = { mom: 1.25, dad: 0.8, grandma: 1.15, teacher: 1.05, office: 0.95, "911": 1 };

  function speak(text, who) {
    if (Sound.isMuted() || !("speechSynthesis" in window)) return;
    try {
      window.speechSynthesis.cancel();
      var u = new SpeechSynthesisUtterance(text);
      u.lang = "en-US"; u.rate = 1; u.pitch = VOICE[who] || 1;
      window.speechSynthesis.speak(u);
    } catch (e) { /* no voice, no problem */ }
  }

  function hush() {
    try { if ("speechSynthesis" in window) window.speechSynthesis.cancel(); } catch (e) { /* ignore */ }
  }

  // ------------------------------------------------------------------ icons

  var SVG = {
    bubble: '<path d="M12 3C6.5 3 2 6.6 2 11c0 2.4 1.3 4.6 3.4 6.1-.2 1.4-.9 2.7-2 3.6 1.9 0 3.7-.7 5.1-1.8 1.1.3 2.3.5 3.5.5 5.5 0 10-3.6 10-8.1S17.5 3 12 3z"/>',
    phone: '<path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1A17 17 0 0 1 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1l-2.3 2.2z"/>',
    mail: '<path d="M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 4-8 5-8-5V6l8 5 8-5v2z"/>',
    person: '<path d="M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zm0 2c-2.7 0-8 1.3-8 4v2h16v-2c0-2.7-5.3-4-8-4z"/>',
    globe: '<g fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.4 3 14.6 0 18M12 3c-3 3.4-3 14.6 0 18"/></g>',
    photo: '<path d="M21 19V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2zM8.5 13.5l2.5 3 3.5-4.5 4.5 6H5l3.5-4.5z"/>',
    camera: '<path d="M9 3 7.2 5H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-3.2L15 3H9zm3 15a5 5 0 1 1 0-10 5 5 0 0 1 0 10z"/>',
    music: '<path d="M12 3v10.6A4 4 0 1 0 14 17V7h4V3h-6z"/>',
    gear: '<path d="M19.4 13a7.5 7.5 0 0 0 0-2l2.1-1.6-2-3.5-2.5 1a7.3 7.3 0 0 0-1.7-1L15 3h-4l-.3 2.9a7.3 7.3 0 0 0-1.7 1l-2.5-1-2 3.5L6.6 11a7.5 7.5 0 0 0 0 2l-2.1 1.6 2 3.5 2.5-1c.5.4 1.1.7 1.7 1L11 21h4l.3-2.9c.6-.3 1.2-.6 1.7-1l2.5 1 2-3.5-2.1-1.6zM13 15.5a3.5 3.5 0 1 1 0-7 3.5 3.5 0 0 1 0 7z"/>',
    info: '<g fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/></g><path d="M11 10.5h2V17h-2zM12 6.6a1.3 1.3 0 1 1 0 2.6 1.3 1.3 0 0 1 0-2.6z"/>',
    trash: '<path d="M6 7h12l-1 13a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2L6 7zm3-4h6l1 2h4v2H4V5h4l1-2z"/>',
    reply: '<path d="M10 9V5l-7 7 7 7v-4.1c5 0 8.5 1.6 11 5.1-1-5-4-10-11-11z"/>',
    flag: '<path d="M14.4 6 14 4H5v17h2v-7h5.6l.4 2h7V6z"/>',
    end: '<path d="M12 9c-1.6 0-3.1.3-4.6.7v3.1c0 .4-.2.7-.6.9-1 .5-1.9 1.1-2.6 1.8-.2.2-.4.3-.7.3s-.5-.1-.7-.3L.3 13c-.2-.2-.3-.4-.3-.7s.1-.5.3-.7A16.9 16.9 0 0 1 12 7c4.6 0 8.7 1.8 11.7 4.6.2.2.3.4.3.7s-.1.5-.3.7l-2.5 2.5c-.2.2-.4.3-.7.3s-.5-.1-.7-.3c-.8-.7-1.6-1.3-2.6-1.8-.3-.2-.6-.5-.6-.9V9.7C15.1 9.3 13.6 9 12 9z"/>',
    back: '<path d="M15.4 4.6 14 3.2 5.2 12l8.8 8.8 1.4-1.4L8 12z"/>',
    del: '<path d="M22 5H8l-6 7 6 7h14V5zm-4 10.6L16.6 17 14 14.4 11.4 17 10 15.6 12.6 13 10 10.4 11.4 9 14 11.6 16.6 9 18 10.4 15.4 13 18 15.6z"/>'
  };

  function svg(name, cls) {
    return '<svg class="' + (cls || "ic") + '" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">' + SVG[name] + "</svg>";
  }

  // Apps on the home screen. "tip" is the pointer hint on Intermediate.
  var APPS = {
    messages: { name: "Messages", icon: "bubble", tip: "texts" },
    phone: { name: "Phone", icon: "phone", tip: "make calls" },
    mail: { name: "Mail", icon: "mail", tip: "your email" },
    web: { name: "Web", icon: "globe" },
    contacts: { name: "Contacts", icon: "person", tip: "real numbers you saved" },
    game: { name: "Pixel Park", emoji: "🌳" },
    photos: { name: "Photos", icon: "photo" },
    camera: { name: "Camera", icon: "camera" },
    music: { name: "Music", icon: "music" },
    settings: { name: "Settings", icon: "gear" }
  };
  var GRID = ["contacts", "game", "photos", "camera", "music", "settings"];
  var DOCK = ["phone", "messages", "mail", "web"];

  // ------------------------------------------------------------------ state

  var contacts = DATA.contacts || [];
  var byId = {};
  contacts.forEach(function (c) { byId[c.id] = c; });

  var S = {
    locked: true,
    app: null,          // which app is open, null = home screen
    id: null,           // which thread / email / contact is open inside it
    tab: "recents",     // Phone app tab
    dial: "",           // Phone keypad
    threads: clone(DATA.threads) || [],
    emails: clone(DATA.emails) || [],
    game: clone(DATA.game) || { chat: [] },
    web: DATA.web || {},
    flags: [],
    ended: false,
    sheet: null,
    call: null,
    banner: null,
    toast: null,
    typing: null,
    sent: {},
    blocked: {},
    revealed: {},
    receipt: {},
    note: {},
    popup: false,       // the scary pop-up is on the web page
    popupDue: false,
    arrived: false,
    gameBlocked: {},
    gameUnread: false,
    playing: false,     // Music app
    flash: false        // Camera app
  };

  // Today's new text / email stays hidden until its notification.
  S.threads.forEach(function (t) { if (t.arrives) t.hidden = true; });
  S.emails.forEach(function (e) { if (e.arrives) e.hidden = true; });

  function thread(id) { return S.threads.filter(function (t) { return t.id === id; })[0]; }
  function email(id) { return S.emails.filter(function (e) { return e.id === id; })[0]; }

  function threadFor(contactId) {
    var t = thread("t_" + contactId);
    if (!t) {
      t = { id: "t_" + contactId, contact: contactId, messages: [], time: "" };
      S.threads.push(t);
    }
    return t;
  }

  function threadName(t) { return t.contact ? byId[t.contact].name : t.number; }

  // ----------------------------------------------------------- scoring hooks

  function act(key, delay) {
    if (S.ended || !key) return "none";
    if (PARTIALS.indexOf(key) >= 0) {
      if (S.flags.indexOf(key) < 0) S.flags.push(key);
      return "flag";
    }
    if (Object.prototype.hasOwnProperty.call(OUT, key)) {
      finish(key, delay);
      return "end";
    }
    return "none";
  }

  function finish(key, delay) {
    if (S.ended) return;
    S.ended = true;
    Sound.alarmOff();
    clearInterval(popupClock);
    root.classList.add("is-ended");
    if (finishBtn) finishBtn.disabled = true;

    var stars = OUT[key];
    if (key === "done") {
      stars = OUT.done || 0;
      S.flags.forEach(function (f) { if (OUT[f] > stars) stars = OUT[f]; });
    }
    later(function () {
      hush();
      S.call = null; S.sheet = null;
      Sound[stars >= 3 ? "win" : stars > 0 ? "meh" : "lose"]();
      S.end = stars >= 3 ? ["🌟", "Nice move!"] : stars > 0 ? ["👍", "Round over"] : ["😬", "Uh oh!"];
      render();
      later(function () {
        form.elements.outcome.value = key;
        form.elements.flags.value = S.flags.join(",");
        form.submit();
      }, 1500);
    }, delay == null ? 700 : delay);
  }

  // ---------------------------------------------------------------- drawing

  root.innerHTML =
    '<div class="tab-bezel">' +
      '<span class="tab-cam" aria-hidden="true"></span>' +
      '<div class="tab-screen">' +
        '<div class="tab-status" aria-hidden="true">' +
          '<span class="tab-clock"></span>' +
          '<span class="tab-icons">' +
            '<svg class="ic-wifi" viewBox="0 0 24 24" fill="currentColor"><path d="M12 18.5 9.5 16a3.5 3.5 0 0 1 5 0L12 18.5zM6.9 13.4a7.2 7.2 0 0 1 10.2 0l-1.6 1.6a5 5 0 0 0-7 0l-1.6-1.6zM4.3 10.8a10.9 10.9 0 0 1 15.4 0l-1.6 1.6a8.6 8.6 0 0 0-12.2 0l-1.6-1.6z"/></svg>' +
            '<span class="tab-pct">87%</span>' +
            '<span class="tab-batt"><span></span></span>' +
          "</span>" +
        "</div>" +
        '<div class="tab-view" id="tab-view"></div>' +
        '<div class="tab-banner" id="tab-banner"></div>' +
        '<div class="tab-overlay" id="tab-overlay"></div>' +
        '<div class="tab-toast" id="tab-toast" role="status"></div>' +
      "</div>" +
      '<button type="button" class="tab-home" data-act="home" aria-label="Home button" ' +
        'data-tip="Home: closes the app and shows all apps"><span></span></button>' +
      '<div class="tab-tiplayer" id="tab-tiplayer" aria-hidden="true"></div>' +
    "</div>";

  var screenEl = root.querySelector(".tab-screen");
  var view = document.getElementById("tab-view");
  var overlay = document.getElementById("tab-overlay");
  var bannerEl = document.getElementById("tab-banner");
  var toastEl = document.getElementById("tab-toast");
  var tipLayer = document.getElementById("tab-tiplayer");
  root.querySelector(".tab-clock").textContent = DATA.time || "4:05";

  function avatar(c, size) {
    var cls = "ava" + (size ? " ava-" + size : "");
    if (!c) return '<span class="' + cls + ' ava-unknown">' + svg("person") + "</span>";
    return '<span class="' + cls + '" style="background:' + esc(c.color) + '">' + esc(initials(c.name)) + "</span>";
  }

  function appIcon(id) {
    var a = APPS[id], badge = badgeFor(id);
    var tip = HINTS && a.tip ? ' data-tip="' + esc(a.name + ": " + a.tip) + '"' : "";
    return '<button type="button" class="app-ico" data-act="open" data-app="' + id + '"' + tip +
      ' aria-label="' + esc(a.name) + (badge ? ", " + badge + " new" : "") + '">' +
      '<span class="app-img ai-' + id + '">' + (a.emoji ? '<span class="app-emoji">' + a.emoji + "</span>" : svg(a.icon)) + "</span>" +
      '<span class="app-name">' + esc(a.name) + "</span>" +
      (badge ? '<span class="app-badge">' + badge + "</span>" : "") +
    "</button>";
  }

  function badgeFor(id) {
    if (id === "messages") return S.threads.filter(function (t) { return !t.hidden && t.unread; }).length;
    if (id === "mail") return S.emails.filter(function (e) { return !e.hidden && !e.removed && e.unread; }).length;
    if (id === "game") return S.gameUnread ? 1 : 0;
    return 0;
  }

  function bar(title, backLabel, extra) {
    return '<header class="bar">' +
      (backLabel ? '<button type="button" class="bar-back" data-act="back">' +
        svg("back") + "<span>" + esc(backLabel) + "</span></button>" : "") +
      '<span class="bar-title">' + esc(title) + "</span>" + (extra || "") +
    "</header>";
  }

  // ----- lock + home

  function drawLock() {
    return '<button type="button" class="lock" data-act="unlock">' +
      '<span class="lock-time">' + esc(DATA.time || "4:05") + "</span>" +
      '<span class="lock-day">' + esc(DATA.day || "Thursday") + "</span>" +
      '<span class="lock-hint">Tap to unlock</span>' +
    "</button>";
  }

  function drawHome() {
    return '<div class="t-home">' +
      '<div class="home-grid">' + GRID.map(appIcon).join("") + "</div>" +
      '<div class="home-dock">' + DOCK.map(appIcon).join("") + "</div>" +
    "</div>";
  }

  // ----- Messages

  function drawMessages() {
    if (S.id) return drawThread(thread(S.id));
    var rows = S.threads.filter(function (t) { return !t.hidden; }).map(function (t) {
      var last = t.messages[t.messages.length - 1] || {};
      var c = t.contact ? byId[t.contact] : null;
      return '<button type="button" class="row" data-act="thread" data-id="' + esc(t.id) + '">' +
        (t.unread ? '<span class="t-dot" aria-label="new"></span>' : '<span class="dot-gap"></span>') +
        avatar(c) +
        '<span class="row-main">' +
          '<span class="row-top"><b>' + esc(threadName(t)) + "</b><time>" + esc(t.time) + "</time></span>" +
          '<span class="row-sub">' + esc(last.image ? "📷 Photo" : last.text || "") + "</span>" +
        "</span>" +
      "</button>";
    }).join("");
    return '<div class="app">' + bar("Messages") + '<div class="scroll">' + rows + "</div></div>";
  }

  function drawThread(t) {
    var c = t.contact ? byId[t.contact] : null;
    var head = '<header class="bar bar-thread">' +
      '<button type="button" class="bar-back" data-act="back" aria-label="Back to Messages"' +
        (HINTS ? ' data-tip="Back"' : "") + ">" + svg("back") + "</button>" +
      '<span class="who">' + avatar(c, "sm") +
        '<span class="who-text"><b>' + esc(threadName(t)) + "</b>" +
        (c ? "" : '<span class="who-warn">Not in your Contacts</span>') + "</span></span>" +
      '<button type="button" class="bar-btn" data-act="call-thread" aria-label="Call"' +
        (HINTS ? ' data-tip="Calls this number"' : "") + ">" + svg("phone") + "</button>" +
      '<button type="button" class="bar-btn" data-act="info" aria-label="Info"' +
        (HINTS ? ' data-tip="Info: block or report"' : "") + ">" + svg("info") + "</button>" +
    "</header>";

    var junk = !c && !S.blocked[t.id]
      ? '<div class="junk">This sender isn\'t in your Contacts. <button type="button" data-act="junk">Report junk</button></div>'
      : "";

    var msgs = t.messages.map(function (m, i) {
      var stamp = m.time ? '<div class="stamp">' + esc(m.time) + "</div>" : "";
      if (m.image) {
        var open = S.revealed[t.id + i];
        return stamp + '<div class="bub them bub-img">' +
          '<div class="scary' + (open ? "" : " is-blurred") + '">' + scaryArt() + "</div>" +
          (open ? "" : '<button type="button" class="reveal" data-act="reveal" data-i="' + i +
            '">This photo may be upsetting.<br>Tap to view</button>') +
        "</div>";
      }
      return stamp + '<div class="bub ' + (m.from === "me" ? "me" : "them") + '">' + esc(m.text) + "</div>";
    }).join("");
    if (S.receipt[t.id]) msgs += '<div class="receipt">' + esc(S.receipt[t.id]) + "</div>";
    if (S.note[t.id]) msgs += '<div class="stamp stamp-note">' + esc(S.note[t.id]) + "</div>";
    if (S.typing === t.id) msgs += '<div class="bub them typing"><i></i><i></i><i></i></div>';

    var chips = chipsFor(t);
    var composer = S.blocked[t.id]
      ? '<div class="composer-note">You blocked this number.</div>'
      : (chips.length
        ? '<div class="chips"' + (HINTS ? ' data-tip="Tap one to send it"' : "") + ">" +
            chips.map(function (ch, i) {
              return '<button type="button" class="t-chip" data-act="send" data-i="' + i + '">' + esc(ch.text) + "</button>";
            }).join("") + "</div>"
        : "") +
        '<div class="fake-input" aria-hidden="true">Text Message</div>';

    return '<div class="app app-thread">' + head + junk +
      '<div class="scroll msgs">' + msgs + "</div>" +
      '<div class="composer">' + composer + "</div></div>";
  }

  // An original picture, not anyone's character: a shadow cat, glowing
  // eyes, and a misspelled account name like the threat posts used.
  function scaryArt() {
    return '<svg viewBox="0 0 200 150" aria-hidden="true">' +
      '<defs><radialGradient id="fog" cx="50%" cy="45%" r="70%"><stop offset="0" stop-color="#3a3f4f"/>' +
      '<stop offset="1" stop-color="#07080c"/></radialGradient></defs>' +
      '<rect width="200" height="150" fill="url(#fog)"/>' +
      '<path d="M60 150c0-38 14-62 40-62s40 24 40 62z" fill="#000"/>' +
      '<path d="M66 96 70 46 92 72h16l22-26 4 50c-6 20-20 30-34 30S72 116 66 96z" fill="#000"/>' +
      '<ellipse cx="86" cy="88" rx="7" ry="4" fill="#ff2a2a"/><ellipse cx="114" cy="88" rx="7" ry="4" fill="#ff2a2a"/>' +
      '<ellipse cx="86" cy="88" rx="2" ry="3" fill="#200"/><ellipse cx="114" cy="88" rx="2" ry="3" fill="#200"/>' +
      '<text x="196" y="144" text-anchor="end" font-size="10" fill="#9aa" font-family="monospace">@c4t.in.th3.h4t</text>' +
    "</svg>";
  }

  function chipsFor(t) {
    if (S.blocked[t.id]) return [];
    var out = [];
    if (t.replies) {
      t.replies.forEach(function (r, i) {
        if (S.sent[t.id + ":r" + i]) return;
        out.push({ key: "r" + i, text: r.text, run: function () {
          if (r.back) { typing(t, r.back); act(r.act, 2400); } else { act(r.act, 1000); }
        } });
      });
    } else if (t.contact && byId[t.contact].text) {
      var c = byId[t.contact];
      if (DATA.tell && !S.sent[t.id + ":tell"]) {
        out.push({ key: "tell", text: DATA.tell.text, run: function () { tellTo(t, c); } });
      }
      if (!S.sent[t.id + ":hi"]) {
        out.push({ key: "hi", text: "👋 Hi!", run: function () {
          typing(t, (DATA.hello_back || {})[c.id] || "Hi! 😊");
        } });
      }
    }
    return out;
  }

  function typing(t, text) {
    later(function () { S.typing = t.id; render(); }, 600);
    later(function () {
      S.typing = null;
      t.messages.push({ from: "them", text: text });
      t.time = "Now";
      Sound.text();
      render();
    }, 1900);
  }

  function tellTo(t, c) {
    var tell = DATA.tell;
    if ((tell.no_reply || []).indexOf(c.id) >= 0) {
      later(function () { S.receipt[t.id] = "Delivered"; render(); }, 700);
      later(function () {
        S.note[t.id] = c.name + " hasn't read it yet.";
        render();
        act(tell.no_reply_act);
      }, 3200);
      return;
    }
    var replies = tell.replies || {};
    typing(t, replies[c.id] || replies["default"] || "Thank you for telling me!");
    act(tell.act, 3000);
  }

  // ----- Phone

  function drawPhone() {
    var body;
    if (S.tab === "keypad") {
      var keys = [["1", ""], ["2", "ABC"], ["3", "DEF"], ["4", "GHI"], ["5", "JKL"], ["6", "MNO"],
        ["7", "PQRS"], ["8", "TUV"], ["9", "WXYZ"], ["*", ""], ["0", "+"], ["#", ""]];
      body = '<div class="keypad">' +
        '<div class="dial-num">' + esc(prettyDial(S.dial)) + "&nbsp;</div>" +
        '<div class="keys">' + keys.map(function (k) {
          return '<button type="button" class="key" data-act="key" data-k="' + k[0] + '"><b>' + k[0] +
            "</b><small>" + k[1] + "</small></button>";
        }).join("") + "</div>" +
        '<div class="dial-row"><span></span>' +
          '<button type="button" class="dial-call" data-act="dial" aria-label="Call"' +
            (HINTS ? ' data-tip="Calls the number you typed"' : "") + ">" + svg("phone") + "</button>" +
          '<button type="button" class="dial-del" data-act="key-del" aria-label="Delete">' + svg("del") + "</button>" +
        "</div></div>";
    } else if (S.tab === "contacts") {
      body = '<div class="scroll">' + contacts.map(function (c) {
        return '<button type="button" class="row" data-act="call-contact" data-id="' + c.id + '">' + avatar(c) +
          '<span class="row-main"><span class="row-top"><b>' + esc(c.name) + "</b></span>" +
          '<span class="row-sub">' + esc(c.phone) + "</span></span></button>";
      }).join("") + "</div>";
    } else {
      var recents = [["mom", "Yesterday"], ["dad", "Tuesday"], ["grandma", "Sunday"]];
      body = '<div class="scroll">' + recents.map(function (r) {
        var c = byId[r[0]];
        return '<button type="button" class="row" data-act="call-contact" data-id="' + c.id + '">' + avatar(c) +
          '<span class="row-main"><span class="row-top"><b>' + esc(c.name) + "</b><time>" + r[1] + "</time></span>" +
          '<span class="row-sub">' + svg("phone", "ic ic-tiny") + " Outgoing call</span></span></button>";
      }).join("") + "</div>";
    }
    var tabs = [["recents", "Recents"], ["contacts", "Contacts"], ["keypad", "Keypad"]];
    return '<div class="app app-phone">' + bar(S.tab === "keypad" ? "Keypad" : S.tab === "contacts" ? "Contacts" : "Recents") +
      body + '<nav class="tabs">' + tabs.map(function (t) {
        return '<button type="button" class="tabs-btn' + (S.tab === t[0] ? " is-on" : "") +
          '" data-act="phone-tab" data-tab="' + t[0] + '">' + t[1] + "</button>";
      }).join("") + "</nav></div>";
  }

  function prettyDial(d) {
    if (d.length === 10) return "(" + d.slice(0, 3) + ") " + d.slice(3, 6) + "-" + d.slice(6);
    return d;
  }

  // ----- Contacts

  function drawContacts() {
    if (S.id) {
      var c = byId[S.id];
      return '<div class="app">' + bar("", "Contacts") +
        '<div class="scroll card">' + avatar(c, "lg") +
          '<div class="card-name">' + esc(c.name) + "</div>" +
          (c.note ? '<div class="card-note">' + esc(c.note) + "</div>" : "") +
          '<div class="card-acts">' +
            (c.text ? '<button type="button" class="card-btn" data-act="message-contact" data-id="' + c.id + '"' +
              (HINTS ? ' data-tip="Text them" data-tip-pos="below"' : "") + ">" + svg("bubble") + "<span>message</span></button>" : "") +
            '<button type="button" class="card-btn" data-act="call-contact" data-id="' + c.id + '"' +
              (HINTS ? ' data-tip="Call them" data-tip-pos="below"' : "") + ">" + svg("phone") + "<span>call</span></button>" +
          "</div>" +
          '<div class="card-rows">' +
            '<div class="card-row"><small>phone</small><span>' + esc(c.phone) + "</span></div>" +
            (c.email ? '<div class="card-row"><small>email</small><span>' + esc(c.email) + "</span></div>" : "") +
          "</div>" +
        "</div></div>";
    }
    return '<div class="app">' + bar("Contacts") + '<div class="scroll">' + contacts.map(function (c) {
      return '<button type="button" class="row" data-act="contact" data-id="' + c.id + '">' + avatar(c) +
        '<span class="row-main"><span class="row-top"><b>' + esc(c.name) + "</b></span>" +
        (c.note ? '<span class="row-sub">' + esc(c.note) + "</span>" : "") + "</span></button>";
    }).join("") + "</div></div>";
  }

  // ----- Mail

  function drawMail() {
    if (S.id) {
      var e = email(S.id);
      var tools = '<span class="bar-gap"></span>' +
        '<button type="button" class="bar-btn" data-act="mail-report" aria-label="Report"' +
          (HINTS ? ' data-tip="Report: tells the email company it\'s a scam"' : "") + ">" + svg("flag") + "</button>" +
        '<button type="button" class="bar-btn" data-act="mail-delete" aria-label="Delete"' +
          (HINTS ? ' data-tip="Delete: throws it away"' : "") + ">" + svg("trash") + "</button>" +
        '<button type="button" class="bar-btn" data-act="mail-reply" aria-label="Reply"' +
          (HINTS ? ' data-tip="Reply: writes back to the sender"' : "") + ">" + svg("reply") + "</button>";
      return '<div class="app">' + bar("", "Inbox", tools) +
        '<div class="scroll mail-read' + (e.loud ? " is-loud" : "") + '">' +
          '<h3 class="mail-subject">' + esc(e.subject) + "</h3>" +
          '<div class="mail-from">' + avatar({ name: e.from_name, color: e.loud ? "#e8a400" : "#6b7a99" }, "sm") +
            '<span><b>' + esc(e.from_name) + '</b> <span class="mail-addr">&lt;' + esc(e.from_addr) + "&gt;</span>" +
            "<small>To: me · " + esc(e.time) + "</small></span></div>" +
          '<div class="mail-body">' + e.body.map(function (p) { return "<p>" + esc(p) + "</p>"; }).join("") +
            (e.link ? '<button type="button" class="mail-link" data-act="mail-link">' + esc(e.link.text) + "</button>" : "") +
          "</div>" +
        "</div></div>";
    }
    var rows = S.emails.filter(function (e) { return !e.hidden && !e.removed; }).map(function (e) {
      return '<button type="button" class="row row-mail" data-act="mail" data-id="' + esc(e.id) + '">' +
        (e.unread ? '<span class="t-dot" aria-label="new"></span>' : '<span class="dot-gap"></span>') +
        '<span class="row-main">' +
          '<span class="row-top"><b>' + esc(e.from_name) + "</b><time>" + esc(e.time) + "</time></span>" +
          '<span class="row-subj">' + esc(e.subject) + "</span>" +
          '<span class="row-sub">' + esc(e.preview) + "</span>" +
        "</span></button>";
    }).join("");
    return '<div class="app">' + bar("Inbox") + '<div class="scroll">' + (rows || '<p class="empty-note">No email</p>') + "</div></div>";
  }

  // ----- Pixel Park

  function drawGame() {
    var g = S.game, pmFrom = g.pm ? g.pm.who : null;
    var lines = g.chat.map(function (l, i) {
      var name = function (who) {
        var tip = HINTS && who === pmFrom && l.kind === "pm" ? ' data-tip="Tap a name for options"' : "";
        return '<button type="button" class="g-name" data-act="player" data-who="' + esc(who) + '"' + tip + ">" + esc(who) + "</button>";
      };
      if (l.kind === "system") return '<div class="g-line g-sys">' + esc(l.text) + "</div>";
      if (l.kind === "pm") return '<div class="g-line g-pm' + (S.gameBlocked[l.who] ? " is-muted" : "") + '">From ' + name(l.who) + ": " + esc(l.text) + "</div>";
      if (l.kind === "me") return '<div class="g-line g-me">' + (l.to ? "To " + esc(l.to) : "You") + ": " + esc(l.text) + "</div>";
      return '<div class="g-line' + (S.gameBlocked[l.who] ? " is-muted" : "") + '">' + name(l.who) + ": " + esc(l.text) + "</div>";
    }).join("");
    return '<div class="app app-game">' +
      '<div class="g-world" aria-hidden="true">' +
        '<div class="g-hud"><span class="g-coins">⭐ 1,240</span><span class="g-map"></span></div>' +
        '<span class="g-spr g-tree1">🌳</span><span class="g-spr g-tree2">🌲</span><span class="g-spr g-house">🏠</span>' +
        '<span class="g-spr g-pond"></span>' +
        '<span class="g-spr g-p1"><em>Bluebird42</em>🐦</span>' +
        '<span class="g-spr g-p2"><em>BlockBuddy</em>🧸</span>' +
        '<span class="g-spr g-you"><em>You</em>🧒</span>' +
      "</div>" +
      '<div class="g-chat">' +
        '<div class="g-tabs"><span class="is-on">All</span><span>Game</span><span>Private</span><span>Clan</span></div>' +
        '<div class="g-lines scroll">' + lines + "</div>" +
        '<button type="button" class="g-input" data-act="game-chat"' + (HINTS ? ' data-tip="Chat with players"' : "") +
          ">Tap here to chat…</button>" +
      "</div></div>";
  }

  function gameLine(line) {
    S.game.chat.push(line);
    render();
  }

  // ----- Web

  var popupClock = null;

  function drawWeb() {
    var w = S.web;
    if (!w.site) {
      return '<div class="app app-web"><div class="url"><span class="url-text">Search or type a website</span></div>' +
        '<div class="scroll web-start"><div class="web-logo">🔎 Search</div>' +
        '<div class="web-tiles"><span>📚 Library</span><span>➗ Math Games</span><span>🌳 Pixel Park</span><span>🌦️ Weather</span></div></div></div>';
    }
    var page = '<div class="url"><span class="url-warn">⚠ Not secure</span><span class="url-text">' + esc(w.site) + "</span></div>" +
      '<div class="scroll web-page">' +
        '<div class="vid"><span class="vid-art">😹</span><span class="vid-bar"><i></i></span></div>' +
        '<div class="vid-title">' + esc(w.video || "") + '</div><div class="vid-meta">1.2M views · 2 days ago</div>' +
        '<div class="vid-more"><span>🐶</span><span>🦖</span><span>🚀</span></div>' +
      "</div>";
    var p = w.popup;
    var pop = S.popup && p
      ? '<div class="scare" role="alertdialog" aria-label="' + esc(p.title) + '"><div class="scare-box">' +
          '<div class="scare-title">' + esc(p.title) + "</div>" +
          p.lines.map(function (l) { return "<p>" + esc(l) + "</p>"; }).join("") +
          '<div class="scare-timer" id="scare-timer">00:' + pad(popupLeft) + "</div>" +
          '<button type="button" class="scare-btn" data-act="popup-update">' + esc(p.button.text) + "</button>" +
          (p.phone ? '<button type="button" class="scare-call" data-act="popup-call">' + esc(p.phone.text) + "</button>" : "") +
        "</div></div>"
      : "";
    return '<div class="app app-web">' + page + pop + "</div>";
  }

  var popupLeft = 59;
  function pad(n) { return n < 10 ? "0" + n : String(n); }

  function popupTick() {
    clearInterval(popupClock);
    popupLeft = (S.web.popup && S.web.popup.timer) || 59;
    popupClock = setInterval(function () {
      popupLeft = popupLeft > 0 ? popupLeft - 1 : 59;
      var el = document.getElementById("scare-timer");
      if (el) el.textContent = "00:" + pad(popupLeft);
    }, 1000);
  }

  function showPopup() {
    S.popupDue = true;
    if (S.app !== "web" || S.ended) return;
    S.popup = true;
    Sound.alarmOn();
    popupTick();
    render();
  }

  // ----- the apps that are just there

  function drawPhotos() {
    var pics = ["🐶", "🏖️", "🎂", "⚽", "🌻", "🐱", "🎄", "🏀", "🍕", "🌈", "🐢", "🎈"];
    return '<div class="app">' + bar("Photos") + '<div class="scroll photos">' +
      pics.map(function (p, i) { return '<span class="pic pic-' + (i % 6) + '">' + p + "</span>"; }).join("") + "</div></div>";
  }

  function drawCamera() {
    return '<div class="app app-camera"><div class="viewfinder' + (S.flash ? " is-flash" : "") + '"><span>📷</span></div>' +
      '<div class="cam-bar"><button type="button" class="shutter" data-act="shutter" aria-label="Take a picture"></button></div></div>';
  }

  function drawMusic() {
    return '<div class="app">' + bar("Music") + '<div class="scroll music">' +
      '<div class="album">🎵</div><div class="song">Happy Song</div><div class="artist">The Pixel Band</div>' +
      '<button type="button" class="music-play" data-act="music">' + (S.playing ? "❚❚" : "▶") + "</button></div></div>";
  }

  function drawSettings() {
    var rows = [["📶", "Wi-Fi", "On"], ["🔵", "Bluetooth", "On"], ["🔔", "Notifications", ""],
      ["🔊", "Sounds", ""], ["⏳", "Screen Time", ""], ["🖼️", "Wallpaper", ""], ["ℹ️", "About", ""]];
    return '<div class="app">' + bar("Settings") + '<div class="scroll">' + rows.map(function (r) {
      return '<div class="row row-static"><span class="set-ico">' + r[0] + '</span><span class="row-main"><span class="row-top"><b>' +
        r[1] + "</b><time>" + r[2] + "</time></span></span></div>";
    }).join("") + "</div></div>";
  }

  var DRAW = { messages: drawMessages, phone: drawPhone, contacts: drawContacts, mail: drawMail,
    game: drawGame, web: drawWeb, photos: drawPhotos, camera: drawCamera, music: drawMusic, settings: drawSettings };

  // ----- overlays: sheets, calls, the end card

  function drawOverlay() {
    if (S.end) {
      return '<div class="end"><div class="end-card"><div class="end-emoji">' + S.end[0] + "</div>" +
        '<div class="end-title">' + S.end[1] + '</div><div class="end-sub">Let\'s see how you did…</div></div></div>';
    }
    if (S.call) {
      var k = S.call;
      return '<div class="call">' +
        '<div class="call-top">' + (k.contact ? avatar(byId[k.contact], "lg") :
          '<span class="ava ava-lg ' + (k.emergency ? "ava-sos" : "ava-unknown") + '">' + (k.emergency ? "SOS" : svg("person")) + "</span>") +
          '<div class="call-name">' + esc(k.name) + "</div>" +
          '<div class="call-status" id="call-status">' + esc(k.status) + "</div></div>" +
        (k.said ? '<div class="call-said">“' + esc(k.said) + "”</div>" : '<div class="call-grid" aria-hidden="true">' +
          "<span>🔇<small>mute</small></span><span>⌨️<small>keypad</small></span><span>🔈<small>speaker</small></span></div>") +
        '<button type="button" class="call-end" data-act="hangup" aria-label="Hang up"' +
          (HINTS ? ' data-tip="Hangs up"' : "") + ">" + svg("end") + "</button>" +
      "</div>";
    }
    if (S.sheet) {
      var sh = S.sheet;
      return '<button type="button" class="sheet-back" data-act="sheet-close" aria-label="Close"></button>' +
        '<div class="sheet" role="dialog">' +
          (sh.title ? '<div class="sheet-title">' + esc(sh.title) + "</div>" : "") +
          (sh.text ? '<div class="sheet-text">' + esc(sh.text) + "</div>" : "") +
          '<div class="sheet-opts">' + sh.options.map(function (o, i) {
            return '<button type="button" class="sheet-opt' + (o.danger ? " is-danger" : "") + '" data-act="sheet-opt" data-i="' + i + '">' + esc(o.label) + "</button>";
          }).join("") + "</div>" +
          '<button type="button" class="sheet-opt sheet-cancel" data-act="sheet-close">Cancel</button>' +
        "</div>";
    }
    return "";
  }

  function sheet(title, text, options) { S.sheet = { title: title, text: text, options: options }; render(); }

  function toast(text) {
    toastEl.textContent = text;
    toastEl.classList.add("is-on");
    clearTimeout(toast.t);
    toast.t = setTimeout(function () { toastEl.classList.remove("is-on"); }, 1800);
  }

  function drawBanner() {
    var n = S.banner;
    if (!n) { bannerEl.innerHTML = ""; return; }
    var a = APPS[n.app] || APPS.messages;
    bannerEl.innerHTML = '<button type="button" class="banner" data-act="banner">' +
      '<span class="app-img ai-' + n.app + ' banner-ico">' + (a.emoji ? '<span class="app-emoji">' + a.emoji + "</span>" : svg(a.icon)) + "</span>" +
      '<span class="banner-main"><span class="banner-top"><span>' + esc(a.name) + "</span><time>now</time></span>" +
      "<b>" + esc(n.title) + '</b><span class="banner-body">' + esc(n.body) + "</span></span></button>";
  }

  // ------------------------------------------------------------- the render

  function render() {
    var html = S.locked ? drawLock() : S.app ? DRAW[S.app]() : drawHome();
    view.innerHTML = html;
    view.className = "tab-view " + (S.locked ? "is-lock" : S.app ? "in-" + S.app : "is-home");
    // dark status-bar text over white apps, white text over wallpaper and calls
    var light = !S.locked && S.app && ["game", "camera"].indexOf(S.app) < 0 && !S.call && !S.end;
    screenEl.classList.toggle("is-light", !!light);
    overlay.innerHTML = drawOverlay();
    overlay.className = "tab-overlay" + (overlay.innerHTML ? " is-on" : "");
    drawBanner();
    var m = view.querySelector(".msgs, .g-lines");
    if (m) m.scrollTop = m.scrollHeight;
    drawHint();
    placeTips();
  }

  // ---------------------------------------------------- Intermediate help

  function viewHint() {
    if (S.locked) return "Tap the screen to unlock the tablet.";
    if (S.call) return "You're on a call. The red button hangs up.";
    if (S.sheet) return "Pick one, or tap Cancel.";
    if (!S.app) return "Tap an app to open it. The round button is Home.";
    if (S.app === "messages") {
      if (!S.id) return "A name means the number is saved in your Contacts. Just a number means it isn't.";
      return thread(S.id).contact ? "This is from someone saved in your Contacts." : "This number is NOT saved in your Contacts.";
    }
    if (S.app === "phone") return S.tab === "keypad" ? "Type a number, then tap the green button to call." : "Tap someone to call them.";
    if (S.app === "contacts") return S.id ? "This is their real, saved number." : "Your Contacts are people whose real numbers you saved.";
    if (S.app === "mail") return S.id ? "Look at the address after the name. Do you know it?" : "Check who each email is from.";
    if (S.app === "game") return "Messages from other players show up in the chat box.";
    if (S.app === "web") return S.popup ? "Websites can't really lock a tablet. The Home button always works." : "You're watching videos.";
    return "This app is just for fun. Press Home to go back.";
  }

  function drawHint() {
    if (!hintEl) return;
    hintEl.innerHTML = (DATA.nudge ? '<p class="tab-hint-nudge"><b>💡 Hint:</b> ' + esc(DATA.nudge) + "</p>" : "") +
      '<p class="tab-hint-view">' + esc(viewHint()) + "</p>";
  }

  var tipsOn = HINTS && store("cs-tips") !== "0";

  function placeTips() {
    tipLayer.innerHTML = "";
    if (!HINTS || !tipsOn || S.ended || S.locked) return;
    var bezel = root.querySelector(".tab-bezel"), box = bezel.getBoundingClientRect();
    var scr = root.querySelector(".tab-screen").getBoundingClientRect();
    var busy = !!(S.sheet || S.call);
    var placed = [];
    var wide = root.classList.contains("tab-wide");

    // the Home button first: it's the one tip that matters on every screen
    var els = Array.prototype.slice.call(root.querySelectorAll("[data-tip]"));
    els.sort(function (a, b) { return b.classList.contains("tab-home") - a.classList.contains("tab-home"); });
    els.forEach(function (el) {
      var inOverlay = overlay.contains(el), isHome = el.classList.contains("tab-home");
      if (busy && !inOverlay && !isHome) return;
      var r = el.getBoundingClientRect();
      if (!r.width || !r.height) return;
      if (!isHome && (r.bottom < scr.top + 20 || r.top > scr.bottom - 4)) return;

      var tip = document.createElement("div");
      tip.className = "tip";
      tip.textContent = el.getAttribute("data-tip");
      tipLayer.appendChild(tip);
      var tw = tip.offsetWidth, th = tip.offsetHeight;
      var cx = r.left + r.width / 2 - box.left, cy = r.top + r.height / 2 - box.top;
      var spots;
      if (isHome && wide) {
        spots = [["left", r.left - box.left - tw - 10, cy - th / 2]];
      } else if (isHome) {
        // portrait: beside the button, inside the bezel, off the hint box
        var x0 = r.right - box.left + 14;
        tip.style.maxWidth = Math.max(90, box.width - x0 - 6) + "px";
        tw = tip.offsetWidth; th = tip.offsetHeight;
        spots = [["right", x0, cy - th / 2]];
      } else {
        var above = [r.top - box.top - th - 9, "above"], below = [r.bottom - box.top + 9, "below"];
        var pos = el.getAttribute("data-tip-pos");
        var order = pos === "below" ? [below, above] : pos === "above" ? [above, below]
          : (r.top - scr.top) < scr.height * 0.4 ? [below, above] : [above, below];
        spots = order.map(function (o) {
          return [o[1], Math.max(4, Math.min(cx - tw / 2, box.width - tw - 4)), o[0]];
        });
      }
      for (var i = 0; i < spots.length; i++) {
        var x = spots[i][1], y = spots[i][2];
        var rect = { l: x, t: y, r: x + tw, b: y + th };
        var clash = placed.some(function (p) { return rect.l < p.r + 3 && rect.r > p.l - 3 && rect.t < p.b + 3 && rect.b > p.t - 3; });
        if (!clash && y > -th && y < box.height) {
          tip.style.left = x + "px";
          tip.style.top = y + "px";
          tip.classList.add("tip-" + spots[i][0]);
          tip.style.setProperty("--ax", Math.max(10, Math.min(tw - 10, cx - x)) + "px");
          placed.push(rect);
          return;
        }
      }
      tipLayer.removeChild(tip);
    });
  }

  // ------------------------------------------------------------- happenings

  function start() {
    S.locked = false;
    if (DATA.start && DATA.start !== "home") openApp(DATA.start);
    render();
    var n = DATA.notify;
    if (n) later(arrive, n.delay || 1600);
  }

  function arrive() {
    var n = DATA.notify;
    if (S.ended || S.arrived || !n) return;
    S.arrived = true;
    var here = false;
    if (n.app === "messages") {
      var t = thread(n.open);
      if (t) {
        t.hidden = false; t.unread = true;
        here = S.app === "messages" && S.id === t.id;
        if (here) t.unread = false;
      }
    } else if (n.app === "mail") {
      var e = email(n.open);
      if (e) { e.hidden = false; e.unread = true; }
    } else if (n.app === "game" && S.game.pm) {
      S.game.chat.push({ kind: "pm", who: S.game.pm.who, text: S.game.pm.text });
      here = S.app === "game";
      S.gameUnread = !here;
    }
    Sound[n.sound || "text"]();
    if (!here) {
      S.banner = n;
      later(function () { if (S.banner === n) { S.banner = null; render(); } }, 6500);
    }
    render();
  }

  function openApp(id) {
    S.app = id; S.id = null; S.sheet = null;
    if (id === "phone") S.tab = S.tab || "recents";
    if (id === "game") S.gameUnread = false;
    if (id === "web" && S.web.popup) {
      if (S.popupDue) { S.popup = true; Sound.alarmOn(); popupTick(); }
      else if (!S.popupTimer) S.popupTimer = later(showPopup, S.web.popup.delay || 2500);
    }
  }

  function goHome() {
    if (S.call) return;
    if (S.sheet) { S.sheet = null; render(); return; }
    if (S.app === "web" && S.popup) {
      S.popup = false;
      Sound.alarmOff();
      clearInterval(popupClock);
      act(S.web.close);
    }
    S.app = null; S.id = null;
    render();
  }

  function goBack() {
    if (S.id) { S.id = null; render(); return; }
    goHome();
  }

  // ----- calls

  function startCall(target) {
    var cfg, k = { status: "calling…", timers: [] };
    if (target.contact) {
      var c = byId[target.contact];
      cfg = CALLS[c.id] || CALLS["default"] || { answer: true, says: "Hi! What's up?" };
      k.contact = c.id; k.name = c.name; k.who = c.id;
    } else if (target.emergency) {
      cfg = CALLS["911"] || {};
      k.emergency = true; k.name = "911"; k.who = "911";
    } else {
      cfg = target.cfg; k.name = target.name;
    }
    S.call = k;
    S.sheet = null;
    render();

    function step(fn, ms) { k.timers.push(later(function () { if (S.call === k) fn(); }, ms)); }
    function status(text) { k.status = text; var el = document.getElementById("call-status"); if (el) el.textContent = text; }
    function connected(said, wait, then) {
      k.said = said; k.status = "00:01"; render();
      var secs = 1;
      k.clock = setInterval(function () { secs++; status("00:" + pad(secs)); }, 1000);
      k.timers.push(k.clock);
      speak(said, k.who);
      step(then, wait);
    }

    Sound.ring();
    if (!cfg) {                                    // a number that goes nowhere
      step(function () { status("Call failed"); Sound.busy(); }, 1400);
      step(hangUp, 3000);
    } else if (target.emergency) {
      step(function () {
        connected("911, what is your emergency?", 2400, function () { act(cfg.act, 300); });
      }, 1600);
    } else if (!target.contact) {                  // the stranger or the "support" line
      step(function () { status("connected"); act(cfg.act, 600); }, 1800);
    } else if (cfg.answer) {
      step(Sound.ring, 2000);
      step(function () {
        var wait = Math.max(2800, Math.min(6500, cfg.says.length * 60));
        connected(cfg.says, wait, function () {
          var res = act(cfg.act, 300);
          if (res !== "end") { status("call ended"); step(hangUp, 900); }
        });
      }, 3600);
    } else {
      step(Sound.ring, 2000);
      step(Sound.ring, 4000);
      step(function () { status("no answer"); Sound.busy(); }, 6000);
      step(function () {
        hangUp();
        toast(k.name + " didn't answer");
        act(cfg.act);
      }, 7600);
    }
  }

  function hangUp() {
    var k = S.call;
    if (!k) return;
    k.timers.forEach(clearTimeout);
    clearInterval(k.clock);
    hush();
    S.call = null;
    render();
  }

  function dialNow() {
    var d = digits(S.dial);
    if (!d) return;
    if (d === "911") return startCall({ emergency: true });
    var c = contacts.filter(function (x) { return digits(x.phone) === d; })[0];
    if (c) return startCall({ contact: c.id });
    var t = S.threads.filter(function (x) { return x.number && digits(x.number) === d; })[0];
    if (t) return startCall({ name: t.number, cfg: { act: t.call } });
    var extra = CALLS.dial || {};
    for (var key in extra) {
      if (Object.prototype.hasOwnProperty.call(extra, key) && digits(key) === d) {
        return startCall({ name: prettyDial(d), cfg: extra[key] });
      }
    }
    startCall({ name: prettyDial(d), cfg: null });
  }

  // ----- game

  function playerMenu(who) {
    var g = S.game, isPm = g.pm && g.pm.who === who;
    var opts = [
      { label: "💬 Send a message", run: function () { gameReplies(who); } },
      { label: "➕ Add friend", run: function () {
        S.sheet = null;
        gameLine({ kind: "system", text: "Friend request sent to " + who + "." });
        if (isPm) act(g.add, 900);
      } },
      { label: "🚩 Report", run: function () {
        sheet("Report " + who, "Why are you reporting them?", [
          "Asking to meet in real life", "Asking for personal info", "Being mean", "Cheating"
        ].map(function (why) {
          return { label: why, run: function () {
            S.sheet = null;
            gameLine({ kind: "system", text: "Thanks! A Pixel Park moderator will look at your report about " + who + "." });
            if (isPm) act(g.report);
          } };
        }));
      } },
      { label: "🚫 Block", danger: true, run: function () {
        S.sheet = null;
        S.gameBlocked[who] = true;
        gameLine({ kind: "system", text: "You blocked " + who + ". You won't see their messages." });
        if (isPm) act(g.block);
      } }
    ];
    sheet(who, null, opts);
  }

  function gameReplies(who) {
    var g = S.game, isPm = g.pm && g.pm.who === who && pmArrived();
    if (S.gameBlocked[who]) { S.sheet = null; toast("You blocked " + who); render(); return; }
    var opts = (isPm ? g.replies : [{ text: "hi!" }, { text: "nice hat" }]).map(function (r) {
      return { label: r.text, run: function () {
        S.sheet = null;
        gameLine({ kind: "me", to: who, text: r.text });
        Sound.game();
        if (r.act) act(r.act, 1000);
      } };
    });
    sheet("Message " + who, null, opts);
  }

  function pmArrived() { return S.game.chat.some(function (l) { return l.kind === "pm"; }); }

  // ------------------------------------------------------------ the clicks

  var ON = {
    unlock: function () { Sound.unlock(); start(); },
    home: goHome,
    back: goBack,
    open: function (d) { Sound.tap(); openApp(d.app); render(); },
    banner: function () {
      var n = S.banner; S.banner = null;
      if (!n) return;
      openApp(n.app);
      if (n.app === "messages" && n.open) { S.id = n.open; thread(n.open).unread = false; }
      if (n.app === "mail" && n.open) openEmail(email(n.open));
      render();
    },
    thread: function (d) { var t = thread(d.id); t.unread = false; S.id = t.id; render(); },
    send: function (d) {
      var t = thread(S.id), ch = chipsFor(t)[+d.i];
      if (!ch) return;
      S.sent[t.id + ":" + ch.key] = true;
      t.messages.push({ from: "me", text: ch.text });
      t.time = "Now";
      Sound.sent();
      render();
      ch.run();
    },
    reveal: function (d) { S.revealed[S.id + d.i] = true; render(); },
    "call-thread": function () {
      var t = thread(S.id);
      if (t.contact) startCall({ contact: t.contact });
      else startCall({ name: t.number, cfg: { act: t.call } });
    },
    info: function () {
      var t = thread(S.id), opts = [];
      if (t.contact) opts.push({ label: "📞 Call " + byId[t.contact].name, run: function () { startCall({ contact: t.contact }); } });
      if (t.block && !S.blocked[t.id]) opts.push({ label: "🚫 Block this " + (t.contact ? "contact" : "number"), danger: true, run: function () { block(t, t.block, "Blocked"); } });
      if (!t.contact && !S.blocked[t.id]) opts.push({ label: "⚠️ Report junk", run: function () { block(t, t.junk, "Reported as junk and blocked"); } });
      if (t.delete) opts.push({ label: "🗑️ Delete conversation", danger: true, run: function () {
        S.threads = S.threads.filter(function (x) { return x !== t; });
        S.id = null; S.sheet = null;
        toast("Conversation deleted");
        render();
        act(t.delete, 900);
      } });
      sheet(threadName(t), t.contact ? "Saved in your Contacts" : "Not in your Contacts", opts);
    },
    junk: function () { var t = thread(S.id); block(t, t.junk, "Reported as junk and blocked"); },
    "sheet-opt": function (d) { var o = S.sheet && S.sheet.options[+d.i]; if (o) o.run(); },
    "sheet-close": function () { S.sheet = null; render(); },
    "phone-tab": function (d) { S.tab = d.tab; render(); },
    key: function (d) { Sound.key(d.k); if (S.dial.length < 15) S.dial += d.k; render(); },
    "key-del": function () { S.dial = S.dial.slice(0, -1); render(); },
    dial: dialNow,
    hangup: hangUp,
    "call-contact": function (d) { startCall({ contact: d.id }); },
    contact: function (d) { S.id = d.id; render(); },
    "message-contact": function (d) {
      var t = threadFor(d.id);
      t.hidden = false;
      S.app = "messages"; S.id = t.id; render();
    },
    mail: function (d) { openEmail(email(d.id)); render(); },
    "mail-report": function () {
      var e = email(S.id);
      sheet("Report as phishing?", "This tells the email company it's a scam, and moves it out of your inbox.", [
        { label: "⚠️ Report", danger: true, run: function () {
          e.removed = true; S.id = null; S.sheet = null;
          toast("Reported. Thanks for keeping email safe!");
          render();
          act(e.report, 900);
        } }
      ]);
    },
    "mail-delete": function () {
      var e = email(S.id);
      e.removed = true; S.id = null;
      toast("Moved to Trash");
      render();
      act(e.delete, 900);
    },
    "mail-reply": function () {
      var e = email(S.id);
      sheet("Reply to " + e.from_name, null, (e.replies || [{ text: "Thanks!" }]).map(function (r) {
        return { label: r.text, run: function () {
          S.sheet = null; Sound.sent(); toast("Sent"); render();
          act(r.act, 900);
        } };
      }));
    },
    "mail-link": function () {
      var e = email(S.id);
      toast("Opening link…");
      act(e.link.act, 1100);
    },
    player: function (d) { playerMenu(d.who); },
    "game-chat": function () {
      var g = S.game, opts = [];
      if (g.pm && pmArrived() && !S.gameBlocked[g.pm.who]) {
        g.replies.forEach(function (r) {
          opts.push({ label: "To " + g.pm.who + ": " + r.text, run: function () {
            S.sheet = null; gameLine({ kind: "me", to: g.pm.who, text: r.text }); Sound.game(); act(r.act, 1000);
          } });
        });
      }
      ["gg!", "anyone want to trade?"].forEach(function (text) {
        opts.push({ label: "Everyone: " + text, run: function () {
          S.sheet = null; gameLine({ kind: "me", text: text }); Sound.game();
        } });
      });
      sheet("Chat", null, opts);
    },
    "popup-update": function () { Sound.alarmOff(); toast("Installing update…"); act(S.web.popup.button.act, 900); },
    "popup-call": function () { Sound.alarmOff(); startCall({ name: S.web.popup.phone.text.replace(/^\D+/, ""), cfg: { act: S.web.popup.phone.act } }); },
    shutter: function () { Sound.shutter(); S.flash = true; render(); later(function () { S.flash = false; render(); }, 180); },
    music: function () { S.playing = !S.playing; render(); }
  };

  function block(t, key, words) {
    S.blocked[t.id] = true; S.sheet = null;
    toast(words);
    render();
    act(key);
  }

  function openEmail(e) {
    S.app = "mail"; S.id = e.id; e.unread = false;
    if (e.open) act(e.open);
  }

  root.addEventListener("click", function (ev) {
    var el = ev.target.closest("[data-act]");
    if (!el || !root.contains(el) || S.ended) return;
    Sound.wake();
    var fn = ON[el.getAttribute("data-act")];
    if (fn) fn(el.dataset, el);
  });

  // ------------------------------------------------------ controls outside

  if (finishBtn) {
    var armed = null;
    finishBtn.addEventListener("click", function () {
      if (S.ended) return;
      Sound.wake();
      if (!armed) {
        finishBtn.textContent = "Tap again to finish";
        finishBtn.classList.add("is-armed");
        armed = setTimeout(function () {
          armed = null;
          finishBtn.textContent = "✋ I'm finished";
          finishBtn.classList.remove("is-armed");
        }, 3000);
        return;
      }
      clearTimeout(armed);
      finishBtn.textContent = "✋ I'm finished";
      hangUp();
      finish("done", 0);
    });
  }

  function soundLabel() {
    if (!soundBtn) return;
    var m = Sound.isMuted();
    soundBtn.textContent = m ? "🔇 Sound off" : "🔊 Sound on";
    soundBtn.setAttribute("aria-pressed", m ? "false" : "true");
  }
  if (soundBtn) {
    soundBtn.addEventListener("click", function () {
      Sound.setMuted(!Sound.isMuted());
      if (!Sound.isMuted()) { Sound.wake(); Sound.tap(); }
      soundLabel();
    });
    soundLabel();
  }

  function tipsLabel() {
    if (!tipsBtn) return;
    tipsBtn.textContent = tipsOn ? "💡 Tips on" : "💡 Tips off";
    tipsBtn.setAttribute("aria-pressed", tipsOn ? "true" : "false");
  }
  if (tipsBtn) {
    tipsBtn.addEventListener("click", function () {
      tipsOn = !tipsOn;
      store("cs-tips", tipsOn ? "1" : "0");
      tipsLabel();
      placeTips();
    });
    tipsLabel();
  }

  // Landscape on a laptop or Chromebook, portrait on a phone.
  function fit() {
    var w = root.clientWidth;
    root.classList.toggle("tab-wide", w >= 600);
    root.classList.toggle("tab-small", w < 340);
    placeTips();
  }
  var fitTimer = null;
  window.addEventListener("resize", function () { clearTimeout(fitTimer); fitTimer = setTimeout(fit, 120); });
  root.addEventListener("scroll", function () { clearTimeout(fitTimer); fitTimer = setTimeout(placeTips, 80); }, true);

  fit();
  render();
  fit();
})();
