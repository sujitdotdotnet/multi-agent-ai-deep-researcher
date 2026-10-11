"""Reusable UI pieces for the "Synthora"-style skin: cards, tags, headers, provenance badges and helpers.

Layout notes: Streamlit gives every keyed container the CSS class `st-key-<key>`, so cards are containers whose key
starts with "card" and are styled by `[class*="st-key-card"]`. Widgets that need a special look (demo question
cards, depth cards, suggestion pills) are targeted the same way through their key.
"""
from __future__ import annotations

from datetime import datetime
from html import escape

import streamlit as st

from src.models.evidence import ORIGIN_LABELS, Origin, Source, SourceAssessment

CSS = """
<style>
:root { --ink:light-dark(#1d2038, #ececf6); --muted:light-dark(#777b91, #a3a6bf); --line:light-dark(#e9eaf1, #2a2d45);
        --paper:light-dark(#f7f7fb, #101120); --surface:light-dark(#ffffff, #181a2d); --violet:#7159dc; --violet-2:#9a78f4;
        --navy:#111329; --green:#27876e; --shadow:0 10px 35px #25234a0b; --soft:light-dark(#f1effd, #241f45); }
/* every colour is a light-dark() pair: Streamlit sets color-scheme from the System / Light / Dark menu */
.block-container { padding-top: 4.5rem; max-width: 1240px; }  /* clears the 3.75rem sticky header */
h1, h2, h3 { letter-spacing: -0.02em; color:var(--ink); }
h1 em, h2 em, .ds-title em { font-style: normal; color:light-dark(#7459d5, color-mix(in srgb, #7459d5 62%, white)); }
[data-testid="stCaptionContainer"], .ds-muted { color:var(--muted); }
[data-testid="stHeader"] { background:light-dark(#f7f7fbd9, #101120d9); backdrop-filter: blur(12px); }
/* cards: keyed containers */
[class*="st-key-card"] { background:var(--surface); border:1px solid light-dark(#ececf3, color-mix(in srgb, #ececf3 16%, #2a2d45)); border-radius:12px; box-shadow:var(--shadow);
                         padding: 18px 22px; }
[class*="st-key-card-flat"] { box-shadow:none; }
.ds-card { background:var(--surface); border:1px solid light-dark(#ececf3, color-mix(in srgb, #ececf3 16%, #2a2d45)); border-radius:12px; box-shadow:var(--shadow); padding:18px 22px; }
/* eyebrow + page heading */
.ds-eyebrow { font-size:10.5px; font-weight:700; letter-spacing:1.6px; color:light-dark(#7660d4, color-mix(in srgb, #7660d4 62%, white)); text-transform:uppercase;
              display:flex; align-items:center; gap:8px; margin-bottom:8px; }
.ds-eyebrow i { display:inline-block; width:7px; height:7px; border-radius:50%; background:#8c70e6; }
.ds-heading { margin: 0 0 1.3rem 0; }
.ds-title { font-family: Manrope, sans-serif; font-weight:800; font-size: 2rem; letter-spacing:-.4px; line-height:1.28;
            margin:.25rem 0 .55rem 0; color:var(--ink); }
.ds-report-head { margin-bottom: 1.6rem; }
.ds-report-head .ds-eyebrow { margin-bottom:16px; }
.ds-report-head .ds-title { margin-bottom:16px; }
.ds-report-head .ds-meta { row-gap:10px; }
[data-baseweb="tab-list"] { gap:24px; flex-wrap:wrap; }
.ds-report-head .ds-title { font-size:1.65rem; font-weight:700; letter-spacing:-.2px; line-height:1.35; max-width: 900px; }
.ds-sub { color:light-dark(#85889a, color-mix(in srgb, #85889a 62%, white)); font-size:.95rem; margin:0; max-width: 760px; line-height:1.55; }
.ds-hero-title { font-family: Manrope, sans-serif; font-weight:800; font-size: clamp(32px,3.6vw,48px); line-height:1.12;
                 letter-spacing:-2px; margin: 1rem 0; color:light-dark(#181a31, #ececf6); }
.ds-hero-title em { font-style:normal; color:light-dark(#7459d5, color-mix(in srgb, #7459d5 62%, white)); }
.ds-lead { max-width:470px; color:light-dark(#777b8f, color-mix(in srgb, #777b8f 62%, white)); font-size:1rem; line-height:1.75; }
.ds-label { font-size:10px; letter-spacing:1px; color:light-dark(#85879a, color-mix(in srgb, #85879a 62%, white)); font-weight:700; text-transform:uppercase; margin: 2px 0 6px 0; }
/* tags & badges */
.ds-tag { display:inline-block; border-radius:4px; padding:3px 7px; font-size:9.5px; font-weight:700; letter-spacing:.5px;
          text-transform:uppercase; vertical-align:middle; }
.ds-complete { background:light-dark(#e9f6f0, color-mix(in srgb, #e9f6f0 13%, #181a2d)); color:light-dark(#39906f, color-mix(in srgb, #39906f 62%, white)); } .ds-running { background:light-dark(#f2edff, color-mix(in srgb, #f2edff 13%, #181a2d)); color:light-dark(#795bd2, color-mix(in srgb, #795bd2 62%, white)); }
.ds-failed { background:light-dark(#fdecec, color-mix(in srgb, #fdecec 13%, #181a2d)); color:light-dark(#c0392b, color-mix(in srgb, #c0392b 62%, white)); } .ds-draft { background:light-dark(#f2f2f5, color-mix(in srgb, #f2f2f5 13%, #181a2d)); color:light-dark(#858795, color-mix(in srgb, #858795 62%, white)); }
.ds-demo-tag { background:light-dark(#fff3dc, color-mix(in srgb, #fff3dc 13%, #181a2d)); color:light-dark(#a7741d, color-mix(in srgb, #a7741d 62%, white)); } .ds-live-tag { background:light-dark(#e4f1ff, color-mix(in srgb, #e4f1ff 13%, #181a2d)); color:light-dark(#3d78b4, color-mix(in srgb, #3d78b4 62%, white)); }
.dr-badge { display:inline-block; padding:2px 7px; border-radius:4px; font-size:10px; font-weight:700; letter-spacing:.4px;
            text-transform:uppercase; margin-right:.3rem; vertical-align:middle; background:light-dark(#f5f4fa, color-mix(in srgb, #f5f4fa 13%, #181a2d)); }
.dr-demo { color:light-dark(#a7741d, color-mix(in srgb, #a7741d 62%, white)); background:light-dark(#fff3dc, color-mix(in srgb, #fff3dc 13%, #181a2d)); } .dr-live { color:light-dark(#27876e, color-mix(in srgb, #27876e 62%, white)); background:light-dark(#e7f5ef, color-mix(in srgb, #e7f5ef 13%, #181a2d)); }
.dr-cache { color:light-dark(#6751cc, color-mix(in srgb, #6751cc 62%, white)); background:light-dark(#f1effd, color-mix(in srgb, #f1effd 13%, #181a2d)); } .dr-upload { color:light-dark(#9a60bd, color-mix(in srgb, #9a60bd 62%, white)); background:light-dark(#f5ebfa, color-mix(in srgb, #f5ebfa 13%, #181a2d)); }
.dr-observed { color:light-dark(#27876e, color-mix(in srgb, #27876e 62%, white)); background:light-dark(#e7f5ef, color-mix(in srgb, #e7f5ef 13%, #181a2d)); } .dr-inferred { color:light-dark(#6751cc, color-mix(in srgb, #6751cc 62%, white)); background:light-dark(#f1effd, color-mix(in srgb, #f1effd 13%, #181a2d)); }
.dr-speculative { color:light-dark(#c0568c, color-mix(in srgb, #c0568c 62%, white)); background:light-dark(#fde9f3, color-mix(in srgb, #fde9f3 13%, #181a2d)); } .dr-flag { color:light-dark(#c0392b, color-mix(in srgb, #c0392b 62%, white)); background:light-dark(#fdecec, color-mix(in srgb, #fdecec 13%, #181a2d)); }
.dr-muted { color:var(--muted); font-size:.86rem; }
/* demo banner */
.ds-banner { display:flex; align-items:center; gap:11px; margin:0 0 18px; padding:10px 14px; border:1px solid light-dark(#e6e0fb, color-mix(in srgb, #e6e0fb 16%, #2a2d45));
             background:light-dark(#f4f1ff, color-mix(in srgb, #f4f1ff 13%, #181a2d)); color:light-dark(#7158cf, color-mix(in srgb, #7158cf 62%, white)); border-radius:8px; font-size:11px; font-weight:700; letter-spacing:.6px; }
.ds-banner span { font-weight:400; letter-spacing:0; color:light-dark(#77768b, color-mix(in srgb, #77768b 62%, white)); }
/* buttons */
[data-testid="stBaseButton-primary"] { border:0; background:linear-gradient(105deg,#7059dc,#8d69e9);
                                       box-shadow:0 5px 12px #755bdc2b; font-weight:700; }
[data-testid="stBaseButton-primary"]:hover { filter:brightness(1.05); transform:translateY(-1px); }
[data-testid="stBaseButton-secondary"] { font-weight:600; color:light-dark(#403e60, color-mix(in srgb, #403e60 62%, white)); border-color:light-dark(#dfdeea, color-mix(in srgb, #dfdeea 16%, #2a2d45)); }
[data-testid="stBaseButton-secondary"]:hover { border-color:light-dark(#a89ae5, color-mix(in srgb, #a89ae5 16%, #2a2d45)); background:light-dark(#faf9ff, color-mix(in srgb, #faf9ff 13%, #181a2d)); color:light-dark(#403e60, color-mix(in srgb, #403e60 62%, white)); }
.stButton button, .stDownloadButton button { font-weight:600; }
/* tabs like the wireframe: underline, violet active */
[data-testid="stTab"] p { color:light-dark(#858798, color-mix(in srgb, #858798 62%, white)); }
[data-testid="stTab"][aria-selected="true"] p { color:light-dark(#694fce, color-mix(in srgb, #694fce 62%, white)); font-weight:700; }
/* sidebar */
[data-testid="stSidebar"] { border-right:1px solid var(--line); }
[data-testid="stSidebarNavLink"] { border-radius:7px; }
[data-testid="stSidebarNavLink"][aria-current="page"] { background:light-dark(#f1effd, color-mix(in srgb, #f1effd 13%, #181a2d)); }
[data-testid="stSidebarNavLink"][aria-current="page"] span { color:light-dark(#644dcc, color-mix(in srgb, #644dcc 62%, white)); font-weight:700; }
[data-testid="stNavSectionHeader"] { font-size:10px !important; font-weight:700; letter-spacing:1.25px; color:light-dark(#a2a4b1, color-mix(in srgb, #a2a4b1 62%, white));
                                     text-transform:uppercase; }
.st-key-side_new button { background:light-dark(#111329, #2d2a5c); color:#fff; border:0; justify-content:flex-start; padding:10px 15px; }
.st-key-side_new button:hover { background:light-dark(#1d2038, #2d2a5c); color:#fff; }
[class*="st-key-recent_"] { margin-bottom: -0.75rem; }
[class*="st-key-recent_"] button { border:0; background:transparent; justify-content:flex-start; color:light-dark(#6e7187, color-mix(in srgb, #6e7187 62%, white));
                                   font-weight:500; padding:6px 9px; min-height:0; }
[class*="st-key-recent_"] button:hover { background:light-dark(#f7f6fc, color-mix(in srgb, #f7f6fc 13%, #181a2d)); color:light-dark(#644dcc, color-mix(in srgb, #644dcc 62%, white)); }
[class*="st-key-recent_"] button p { white-space:nowrap; overflow:hidden; text-overflow:ellipsis; font-size:12.5px; }
.ds-profile { display:flex; align-items:center; gap:10px; padding:6px 2px; }
.ds-avatar { width:34px; height:34px; display:grid; place-items:center; border-radius:50%; background:light-dark(#e9e5fa, color-mix(in srgb, #e9e5fa 13%, #181a2d));
             color:light-dark(#6754c4, color-mix(in srgb, #6754c4 62%, white)); font-weight:700; font-size:12px; flex:0 0 34px; overflow:hidden; }
.ds-avatar img { width:100%; height:100%; object-fit:cover; }
.ds-profile b { display:block; font-size:12.5px; } .ds-profile small { display:block; color:light-dark(#999bad, color-mix(in srgb, #999bad 62%, white)); font-size:11px; }
/* selectable cards built from radios (demo questions, depth): each option wrapper becomes a card */
[class*="st-key-pick_"] [data-testid="stElementContainer"], [class*="st-key-pick_"] .stRadio { width: 100%; }
[class*="st-key-pick_"] [role="radiogroup"] { gap: 9px; width: 100%; }
[class*="st-key-pick_"] [role="radiogroup"] > div { flex: 1 1 0; background:var(--surface); border:1px solid light-dark(#e6e5ed, color-mix(in srgb, #e6e5ed 16%, #2a2d45)); border-radius:8px;
                                                   padding:11px 14px; margin:0; cursor:pointer; transition:.15s; }
[class*="st-key-pick_"] [role="radiogroup"] > div:hover { border-color:light-dark(#c9beef, color-mix(in srgb, #c9beef 16%, #2a2d45)); }
[class*="st-key-pick_"] [role="radiogroup"] > div[data-selected="true"] { border-color:#9d89e2; background:light-dark(#f9f7ff, color-mix(in srgb, #f9f7ff 13%, #181a2d));
                                                                         box-shadow:inset 0 0 0 1px #9d89e2; }
[class*="st-key-pick_"] [data-testid="stRadioOption"] { width:100%; margin:0; }
[class*="st-key-pick_"] [data-testid="stRadioOption"] > div > div:first-child { display:none; }  /* hide the dot */
[class*="st-key-pick_"] [data-testid="stRadioOption"] p { font-weight:600; font-size:.92rem; color:light-dark(#25283e, #ececf6); }
[class*="st-key-pick_"] [data-testid="stRadioCaption"] { padding-left:0; margin-left:0; }
[class*="st-key-pick_"] [data-testid="stRadioCaption"] p { font-size:11.5px; }
.st-key-pick_demo [role="radiogroup"] { flex-direction: column; align-items: stretch; }
.st-key-pick_demo [role="radiogroup"] > div { width: 100%; }
.st-key-pick_demo [role="radiogroup"] > div[data-selected="true"] [data-testid="stRadioOption"] p::before {
  content:"✓  "; color:light-dark(#7159dc, color-mix(in srgb, #7159dc 62%, white)); }
/* suggestion pills */
[class*="st-key-sugg_"] button { border:1px solid light-dark(#e8e7ef, color-mix(in srgb, #e8e7ef 16%, #2a2d45)); background:light-dark(#fafaff, color-mix(in srgb, #fafaff 13%, #181a2d)); border-radius:20px; padding:4px 12px;
                                 color:light-dark(#676a7e, color-mix(in srgb, #676a7e 62%, white)); font-weight:500; min-height:0; }
[class*="st-key-sugg_"] button:hover { background:light-dark(#f1edff, color-mix(in srgb, #f1edff 13%, #181a2d)); border-color:light-dark(#cfc5f2, color-mix(in srgb, #cfc5f2 16%, #2a2d45)); color:light-dark(#674fc4, color-mix(in srgb, #674fc4 62%, white)); }
[class*="st-key-sugg_"] button p { font-size:12px; }
/* hero visual (landing) */
.ds-visual { position:relative; height:400px; display:grid; place-items:center;
             background:radial-gradient(ellipse,light-dark(#eee9ff, color-mix(in srgb, #eee9ff 13%, #181a2d)) 0%,light-dark(#f4f1ff, color-mix(in srgb, #f4f1ff 13%, #181a2d)) 37%,transparent 69%); }
.ds-orb { position:absolute; border:1px solid light-dark(#d8d0f6, color-mix(in srgb, #d8d0f6 16%, #2a2d45)); border-radius:50%; transform:rotate(-22deg); }
.ds-orb.one { height:275px; width:420px; } .ds-orb.two { height:345px; width:490px; border-color:light-dark(#e5e0f8, color-mix(in srgb, #e5e0f8 16%, #2a2d45)); }
.ds-vcard { position:relative; z-index:2; width:min(390px,90%); border:1px solid light-dark(#e7e5f2, color-mix(in srgb, #e7e5f2 16%, #2a2d45)); background:var(--surface); border-radius:13px;
            padding:20px 22px; box-shadow:0 20px 60px #49406e1c; }
.ds-vtop { font-size:9px; font-weight:700; letter-spacing:1px; color:light-dark(#77798c, color-mix(in srgb, #77798c 62%, white)); }
.ds-dot { display:inline-block; background:#41bb94; width:7px; height:7px; border-radius:50%; margin-right:6px; }
.ds-vlive { float:right; color:light-dark(#3a9c7b, color-mix(in srgb, #3a9c7b 62%, white)); }
.ds-vcard h3 { font:700 15px/1.5 Manrope, sans-serif; margin:18px 0; }
.ds-vrow { border-top:1px solid light-dark(#f0eff5, color-mix(in srgb, #f0eff5 16%, #2a2d45)); display:flex; align-items:center; padding:10px 0; font-size:12px; gap:10px; }
.ds-vrow b { margin-left:auto; color:light-dark(#7e7e91, color-mix(in srgb, #7e7e91 62%, white)); font-size:11px; font-weight:500; }
.ds-vfoot { border-top:1px solid light-dark(#f0eff5, color-mix(in srgb, #f0eff5 16%, #2a2d45)); padding-top:12px; color:light-dark(#888a9b, color-mix(in srgb, #888a9b 62%, white)); font-size:11px; display:flex; justify-content:space-between; }
.ds-chip { position:absolute; z-index:3; background:var(--surface); border:1px solid light-dark(#eeedf4, color-mix(in srgb, #eeedf4 16%, #2a2d45)); border-radius:8px; padding:10px 13px;
           box-shadow:0 7px 25px #3b376116; font-size:11px; font-weight:700; color:light-dark(#6254b5, color-mix(in srgb, #6254b5 62%, white)); }
.ds-chip.a { top:4px; right:-6px; } .ds-chip.b { bottom:2px; left:-6px; color:light-dark(#4b8175, color-mix(in srgb, #4b8175 62%, white)); }
.ds-foot { display:flex; justify-content:space-between; border-top:1px solid light-dark(#e8e7ef, color-mix(in srgb, #e8e7ef 16%, #2a2d45)); padding:18px 0; color:light-dark(#999aaa, color-mix(in srgb, #999aaa 62%, white));
           font-size:10px; letter-spacing:1px; margin-top:8px; }
.ds-foot div { display:flex; gap:30px; color:light-dark(#73768b, color-mix(in srgb, #73768b 62%, white)); font-size:12px; letter-spacing:0; }
.ds-proof { display:flex; align-items:center; gap:13px; margin-top:26px; font-size:12px; }
.ds-proof small { display:block; color:light-dark(#9294a3, color-mix(in srgb, #9294a3 62%, white)); margin-top:3px; font-size:11px; }
.ds-avatars { display:flex; } .ds-avatars span { width:26px; height:26px; display:grid; place-items:center; margin-right:-6px;
  border:2px solid light-dark(#fff, color-mix(in srgb, #fff 16%, #2a2d45)); border-radius:50%; background:light-dark(#d9d1f5, color-mix(in srgb, #d9d1f5 13%, #181a2d)); color:light-dark(#5949af, color-mix(in srgb, #5949af 62%, white)); font-size:10px; font-weight:700; }
.ds-avatars span:nth-child(2) { background:light-dark(#c9e3dc, color-mix(in srgb, #c9e3dc 13%, #181a2d)); color:light-dark(#387665, color-mix(in srgb, #387665 62%, white)); } .ds-avatars span:nth-child(3) { background:light-dark(#f1d8ca, color-mix(in srgb, #f1d8ca 13%, #181a2d)); color:light-dark(#875640, color-mix(in srgb, #875640 62%, white)); }
.ds-avatars span:nth-child(4) { background:light-dark(#eeeef4, color-mix(in srgb, #eeeef4 13%, #181a2d)); color:light-dark(#72768b, color-mix(in srgb, #72768b 62%, white)); }
.ds-feature { padding:22px; border:1px solid var(--line); background:var(--surface); border-radius:11px; height:100%; }
.ds-feature h3 { font:700 15px Manrope, sans-serif; margin:12px 0 6px; }
.ds-feature p { font-size:13px; line-height:1.7; color:light-dark(#84879a, color-mix(in srgb, #84879a 62%, white)); margin:0; }
/* agent icons, rows and activity timeline */
.ds-icon { width:28px; height:28px; border-radius:8px; display:grid; place-items:center; font-size:13px; flex:0 0 28px; }
.ds-purple { background:light-dark(#eee9ff, color-mix(in srgb, #eee9ff 13%, #181a2d)); color:light-dark(#7858d2, color-mix(in srgb, #7858d2 62%, white)); } .ds-blue { background:light-dark(#e4f1ff, color-mix(in srgb, #e4f1ff 13%, #181a2d)); color:light-dark(#4181bf, color-mix(in srgb, #4181bf 62%, white)); }
.ds-green { background:light-dark(#e3f5ed, color-mix(in srgb, #e3f5ed 13%, #181a2d)); color:light-dark(#31946d, color-mix(in srgb, #31946d 62%, white)); } .ds-indigo { background:light-dark(#e8e8ff, color-mix(in srgb, #e8e8ff 13%, #181a2d)); color:light-dark(#6864c5, color-mix(in srgb, #6864c5 62%, white)); }
.ds-gold { background:light-dark(#fff2d9, color-mix(in srgb, #fff2d9 13%, #181a2d)); color:light-dark(#b78127, color-mix(in srgb, #b78127 62%, white)); } .ds-pink { background:light-dark(#fde9f3, color-mix(in srgb, #fde9f3 13%, #181a2d)); color:light-dark(#c0568c, color-mix(in srgb, #c0568c 62%, white)); } .ds-teal { background:light-dark(#e0f4f3, color-mix(in srgb, #e0f4f3 13%, #181a2d)); color:light-dark(#389592, color-mix(in srgb, #389592 62%, white)); }
.ds-agent { display:flex; align-items:center; gap:11px; border-top:1px solid light-dark(#f0eff4, color-mix(in srgb, #f0eff4 16%, #2a2d45)); padding:11px 0; }
.ds-agent:first-of-type { border-top:0; }
.ds-agent > div { min-width:0; } .ds-agent b { display:block; font-size:13px; }
.ds-agent small { display:block; font-size:11.5px; color:light-dark(#9092a0, color-mix(in srgb, #9092a0 62%, white)); margin-top:3px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.ds-state { margin-left:auto; font-size:11px; color:light-dark(#9294a4, color-mix(in srgb, #9294a4 62%, white)); white-space:nowrap; }
.ds-agent.done .ds-state { color:light-dark(#328e70, color-mix(in srgb, #328e70 62%, white)); } .ds-agent.working .ds-state { color:light-dark(#7559d3, color-mix(in srgb, #7559d3 62%, white)); font-weight:700; }
.ds-agent.failed .ds-state { color:light-dark(#c0392b, color-mix(in srgb, #c0392b 62%, white)); }
.ds-act { position:relative; display:flex; gap:11px; padding:12px 0 6px 4px; }
.ds-act:not(:last-child)::before { content:''; position:absolute; top:24px; left:7px; bottom:-8px; width:1px; background:light-dark(#e9e6f4, color-mix(in srgb, #e9e6f4 13%, #181a2d)); }
.ds-act > i { position:relative; z-index:1; width:8px; height:8px; flex:0 0 8px; background:#8d76db; border:2px solid light-dark(#eee9fb, color-mix(in srgb, #eee9fb 16%, #2a2d45));
              border-radius:50%; margin-top:4px; }
.ds-act.current > i { background:#55b391; }
.ds-act b { display:block; font-size:12px; } .ds-act small { display:block; font-size:11px; color:light-dark(#898b9c, color-mix(in srgb, #898b9c 62%, white)); margin:3px 0; }
.ds-act time { font-size:10px; color:light-dark(#aaa, color-mix(in srgb, #aaa 62%, white)); }
.ds-progress { height:6px; background:light-dark(#eeeaf8, color-mix(in srgb, #eeeaf8 13%, #181a2d)); border-radius:6px; margin-top:16px; overflow:hidden; }
.ds-progress i { display:block; height:100%; background:linear-gradient(90deg,#7159dc,#a582ee); border-radius:6px; }
.ds-progress-cap { display:flex; justify-content:space-between; margin-top:7px; font-size:11px; color:light-dark(#888a9c, color-mix(in srgb, #888a9c 62%, white)); }
.ds-meta { display:flex; flex-wrap:wrap; align-items:center; row-gap:4px; color:light-dark(#87899a, color-mix(in srgb, #87899a 62%, white)); font-size:13px; line-height:1.6; }
.ds-meta span + span::before { content:"·"; margin:0 10px; color:light-dark(#c2c3ce, color-mix(in srgb, #c2c3ce 62%, white)); }
.ds-live { font-size:10.5px; color:light-dark(#328f72, color-mix(in srgb, #328f72 62%, white)); background:light-dark(#e7f5ef, color-mix(in srgb, #e7f5ef 13%, #181a2d)); border-radius:20px; padding:7px 12px; font-weight:700;
           display:inline-flex; align-items:center; gap:7px; }
.ds-live i { width:7px; height:7px; border-radius:50%; background:#41bb94; display:inline-block; }
/* results */
.ds-finding { display:flex; gap:12px; border-top:1px solid light-dark(#f0eff4, color-mix(in srgb, #f0eff4 16%, #2a2d45)); padding:12px 0; }
.ds-finding > span { font:700 12px Manrope, sans-serif; color:light-dark(#9079de, color-mix(in srgb, #9079de 62%, white)); }
.ds-finding p { font-size:13.5px; line-height:1.65; color:light-dark(#676a7b, color-mix(in srgb, #676a7b 62%, white)); margin:0; } .ds-finding b { color:light-dark(#303249, #ececf6); }
.ds-stat { display:flex; justify-content:space-between; font-size:13px; color:light-dark(#777a8e, color-mix(in srgb, #777a8e 62%, white)); padding:6px 0; }
.ds-stat b { color:light-dark(#303249, #ececf6); } .ds-stat .ok { color:light-dark(#328e70, color-mix(in srgb, #328e70 62%, white)); } .ds-stat .warn { color:light-dark(#b78127, color-mix(in srgb, #b78127 62%, white)); }
.ds-pills { display:flex; flex-wrap:wrap; gap:6px; padding-bottom:4px; } .ds-pills span { background:light-dark(#f5f3fb, color-mix(in srgb, #f5f3fb 13%, #181a2d)); color:light-dark(#77718c, color-mix(in srgb, #77718c 62%, white)); padding:5px 8px;
            border-radius:5px; font-size:11.5px; }
.ds-meter { height:6px; background:light-dark(#efedf6, color-mix(in srgb, #efedf6 13%, #181a2d)); border-radius:6px; margin:16px 0 7px; } .ds-meter i { display:block; height:100%;
            background:#62b798; border-radius:6px; }
.ds-num { display:block; font:700 26px Manrope, sans-serif; color:light-dark(#e0daf4, #3b3766); margin-bottom:8px; }
/* library rows */
.ds-row-title b { display:block; font-size:14px; color:light-dark(#34364b, #ececf6); } .ds-row-title small { display:block; font-size:12px; color:light-dark(#9698a6, color-mix(in srgb, #9698a6 62%, white)); margin-top:3px; }
.ds-cell { font-size:13px; color:light-dark(#727589, color-mix(in srgb, #727589 62%, white)); padding-top:6px; }
.ds-colhead { font-size:10px; letter-spacing:.8px; color:light-dark(#9a9baa, color-mix(in srgb, #9a9baa 62%, white)); font-weight:700; padding:4px 0 0 0; }
[data-testid="stMetricLabel"] p { font-size:11px !important; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); }
[data-testid="stExpander"] details { border-radius:10px; background:var(--surface); }
[data-testid="stExpander"] summary p { font-weight:600; }
hr { border-color:var(--line) !important; }
</style>
"""

ORIGIN_CLASS = {Origin.DEMO: "dr-demo", Origin.LIVE: "dr-live", Origin.CACHE: "dr-cache", Origin.UPLOAD: "dr-upload"}
AGREEMENT_COLORS = {"strong": "green", "moderate": "blue", "single_source": "gray", "mixed": "orange", "contested": "red"}
QUALITY_COLORS = {"high": "green", "medium": "blue", "low": "orange", "unknown": "gray"}
STATUS_ICON = {"pending": "○", "running": "◐", "completed": "●", "failed": "✕", "skipped": "–"}
AGENT_TITLES = {"planner": "Research Planner", "retriever": "Contextual Retriever", "source_evaluator": "Source Evaluation",
                "critical_analyst": "Critical Analysis", "gap_analyst": "Gap & Follow-up",
                "insight_generator": "Insight Generation", "data_visualizer": "Data Visualization", "report_builder": "Report Builder",
                "orchestrator": "Orchestrator"}
# icon, colour class, what the agent does (shown while it is queued)
AGENT_INFO = {
    "planner": ("⌕", "ds-purple", "Splits the question into research threads and queries"),
    "retriever": ("◎", "ds-blue", "Searches web, academic and document sources"),
    "source_evaluator": ("▤", "ds-indigo", "Rates relevance, credibility and freshness"),
    "critical_analyst": ("⌁", "ds-green", "Links claims to passages and finds contradictions"),
    "gap_analyst": ("◈", "ds-gold", "Finds gaps and decides whether to dig deeper"),
    "insight_generator": ("✧", "ds-pink", "Finds patterns, implications and hypotheses"),
    "data_visualizer": ("▥", "ds-blue", "Charts extracted values and links every point to its source"),
    "report_builder": ("✓", "ds-teal", "Writes the cited report and validates citations"),
}
STATUS_TAG = {"completed": ("Complete", "ds-complete"), "running": ("In progress", "ds-running"),
              "failed": ("Failed", "ds-failed")}
DEPTH_LABELS = {"quick": "Quick", "standard": "Standard", "deep": "Deep"}


def inject_css() -> None:
    # no blank lines allowed inside CSS: Markdown would end the <style> block at the first one
    st.markdown(CSS, unsafe_allow_html=True)


def html(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)


def eyebrow(text: str, center: bool = False) -> str:
    style = ' style="justify-content:center"' if center else ""
    return f'<div class="ds-eyebrow"{style}><i></i>{escape(text)}</div>'


def page_header(eyebrow_text: str, title: str, subtitle: str = "", accent: str = "") -> None:
    """Wireframe page heading: dotted eyebrow, bold title with an optional violet accent, muted lead."""
    accent_html = f" <em>{escape(accent)}</em>" if accent else ""
    lead = f'<p class="ds-sub">{escape(subtitle)}</p>' if subtitle else ""
    html(f'<div class="ds-heading">{eyebrow(eyebrow_text)}<div class="ds-title">{escape(title)}{accent_html}</div>{lead}</div>')


def card(key: str, flat: bool = False):
    """A white rounded card (a keyed container styled via CSS)."""
    return st.container(key=f"card-{'flat-' if flat else ''}{key}")


def tag(text: str, css: str) -> str:
    return f'<span class="ds-tag {css}">{escape(text)}</span>'


def status_tag(status: str) -> str:
    label, css = STATUS_TAG.get(status, (status, "ds-draft"))
    return tag(label, css)


def mode_tag(mode: str) -> str:
    return tag("Demo", "ds-demo-tag") if mode == "demo" else tag("Live", "ds-live-tag")


def ago(when: datetime | None) -> str:
    if when is None:
        return ""
    seconds = (datetime.now() - when).total_seconds()
    if seconds < 60:
        return "just now"
    if seconds < 3600:
        return f"{int(seconds // 60)} min ago"
    if seconds < 86400:
        hours = int(seconds // 3600)
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    if seconds < 172800:
        return "yesterday"
    return f"{when:%b %d, %Y}"


def badge(text: str, css: str) -> str:
    return f'<span class="dr-badge {css}">{escape(text)}</span>'


def origin_badge(origin: Origin) -> str:
    return badge(ORIGIN_LABELS[origin].upper(), ORIGIN_CLASS[origin])


def label_badge(label: str) -> str:
    return badge(label.upper(), f"dr-{label}")


def demo_banner(mode: str) -> None:
    if mode == "demo":
        html('<div class="ds-banner">DEMO PREVIEW <span>Synthetic sample dataset: every source is fictional. Use it to '
             'explore the workflow, not as evidence. Sign in and switch to Live research for real sources.</span></div>')


def source_header(source: Source, assessment: SourceAssessment | None, number: int | None = None) -> str:
    who = source.publisher or ", ".join(source.authors[:2]) or "Unknown publisher"
    when = source.published_date.strftime("%d %b %Y") if source.published_date else "date unknown"
    prefix = f"[{number}] " if number else ""
    quality = assessment.evidence_quality.value if assessment else "unknown"
    return f"{prefix}{source.title} · {who} · {when} · quality {quality}"


def link_for(source: Source):
    if not source.url:
        return None
    label = "Open source (synthetic placeholder URL)" if source.is_synthetic else "Open original source"
    return label, source.url


def flags_html(assessment: SourceAssessment | None) -> str:
    if not assessment or not assessment.flags:
        return ""
    return " ".join(badge(f.replace("_", " "), "dr-flag") for f in assessment.flags)
