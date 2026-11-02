---
name: AstroVerse
description: A calm, personal observatory for exploring Vedic astrology.
colors:
  ink: "#070a17"
  surface: "#11182a"
  surface-raised: "#182238"
  surface-soft: "#202d45"
  line: "#35435d"
  text: "#f2f3f8"
  muted: "#b8c2d3"
  quiet: "#95a2b8"
  violet: "#aaa5ff"
  violet-strong: "#7770ed"
  gold: "#edc981"
typography:
  display:
    fontFamily: "Manrope Variable, Manrope, sans-serif"
    fontSize: "clamp(3rem, 7vw, 5.5rem)"
    fontWeight: 650
    lineHeight: 0.99
    letterSpacing: "-0.045em"
  body:
    fontFamily: "DM Sans Variable, DM Sans, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.6
rounded:
  sm: "10px"
  md: "14px"
  card: "16px"
spacing:
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "40px"
components:
  button-primary:
    backgroundColor: "{colors.violet-strong}"
    textColor: "#ffffff"
    rounded: "{rounded.sm}"
    padding: "0 20px"
    height: "48px"
  surface-card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    rounded: "{rounded.card}"
    padding: "24px"
  form-control:
    backgroundColor: "{colors.surface-soft}"
    textColor: "{colors.text}"
    rounded: "{rounded.sm}"
    padding: "12px"
    height: "48px"
---

## Overview

AstroVerse is a personal Vedic astrology product for chart exploration and daily guidance. Its visual world is a quiet observatory: deep night surfaces, restrained celestial details, clear chart typography, and warm chart-paper surfaces where planetary diagrams need focus.

## Colors

Use ink for the page canvas and the three surface tones for content hierarchy. Violet is the main action and active-state color. Gold is reserved for chart accents and traditional timing. Keep text readable; use muted and quiet colors for secondary information rather than reducing opacity on important copy.

## Typography

Use self-hosted Manrope Variable for headings and controls and DM Sans Variable for reading text. Keep headings compact and strong, body copy relaxed and readable, and chart measurements aligned with tabular numerals when shown.

## Layout

Use a centered content width around 1200px for dashboard screens. Keep page titles and their actions together; separate major sections with generous vertical space. On narrow screens, stack columns and keep horizontal chart selectors scrollable with their active item visible.

## Elevation & Depth

Prefer tonal surface changes and fine borders. Use one soft, offset shadow for a focused raised surface. Avoid decorative blur and glow effects. The star field is a low-contrast background texture and must never compete with the current task.

## Shapes

Cards use 16px corners, controls use 10px, and small selection chips may be fully rounded. Inputs need a clear visible focus ring. Do not place controls inside nested decorative cards.

## Components

Primary buttons use violet with white text and a minimum 48px height. Form fields use the raised slate surface with persistent labels. Navigation uses text labels with consistent line icons and a distinct active state. Birth charts use warm parchment tones so the diagram remains legible against the night interface.

## Do's and Don'ts

- Do preserve precise Vedic terminology and explain unfamiliar abbreviations near their first use.
- Do distinguish calculated chart facts from interpretive commentary.
- Do keep horoscope, chart, and timing pages scannable and responsive.
- Don't use emoji or decorative glyphs as interface icons.
- Don't use gradient text, excessive card nesting, or low-contrast microcopy.
- Don't imply astrology readings guarantee specific outcomes.
