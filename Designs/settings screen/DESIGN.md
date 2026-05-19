---
name: Aegis Enterprise
colors:
  surface: '#f7f9fb'
  surface-dim: '#d8dadc'
  surface-bright: '#f7f9fb'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f4f6'
  surface-container: '#eceef0'
  surface-container-high: '#e6e8ea'
  surface-container-highest: '#e0e3e5'
  on-surface: '#191c1e'
  on-surface-variant: '#45464d'
  inverse-surface: '#2d3133'
  inverse-on-surface: '#eff1f3'
  outline: '#76777d'
  outline-variant: '#c6c6cd'
  surface-tint: '#565e74'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#131b2e'
  on-primary-container: '#7c839b'
  inverse-primary: '#bec6e0'
  secondary: '#003ec6'
  on-secondary: '#ffffff'
  secondary-container: '#0052fe'
  on-secondary-container: '#dfe3ff'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#0b1c30'
  on-tertiary-container: '#75859d'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dae2fc'
  primary-fixed-dim: '#bec6e0'
  on-primary-fixed: '#131b2e'
  on-primary-fixed-variant: '#3f465b'
  secondary-fixed: '#dde1ff'
  secondary-fixed-dim: '#b7c4ff'
  on-secondary-fixed: '#001452'
  on-secondary-fixed-variant: '#0038b6'
  tertiary-fixed: '#d3e3ff'
  tertiary-fixed-dim: '#b7c7e2'
  on-tertiary-fixed: '#0b1c30'
  on-tertiary-fixed-variant: '#38485e'
  background: '#f7f9fb'
  on-background: '#191c1e'
  surface-variant: '#e0e3e5'
  success-pulse: '#4ade80'
  urgent-error: '#ba1a1a'
  warning-container: '#ffdad6'
typography:
  display-lg:
    fontFamily: Hanken Grotesk
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Hanken Grotesk
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Hanken Grotesk
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.05em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 32px
  gutter: 24px
  margin-page: 40px
  sidebar-width: 280px
  container-max: 1440px
---

## Brand & Style
Aegis Enterprise is a high-performance management interface designed for technical operations and AI-driven workflows. The brand personality is **authoritative, precise, and sophisticated**, targeting enterprise-level decision-makers and system administrators.

The design style is **Corporate / Modern** with a strong emphasis on **Tonal Layering**. It utilizes a deep, command-center aesthetic for navigation sidebars contrasted against a clean, air-filled canvas for data analysis. The visual language conveys reliability and high-tech intelligence through sharp typography and a disciplined, data-dense layout.

## Colors
The palette is rooted in a professional "Deep Navy" (`primary`) which anchors the global navigation and high-priority AI containers. A vibrant "System Blue" (`secondary`) is used exclusively for primary actions, progress indicators, and active states to provide clear interactive affordance.

Neutral surfaces utilize a cool-grey foundation (`#f7f9fb`) to reduce eye strain during long sessions. Accent colors like `urgent-error` are reserved for critical system patches and high-priority task badges, ensuring they stand out immediately against the monochromatic data tables.

## Typography
The system uses a tri-font approach to categorize information. **Hanken Grotesk** is the primary display face, providing a modern, sharp look for headers and KPIs. **Inter** serves as the workhorse for all body copy and descriptions due to its exceptional legibility at small sizes. **JetBrains Mono** is utilized for labels, status chips, and technical IDs to evoke a precise, developer-centric feel.

On mobile devices, `display-lg` should scale down to 36px to maintain visual hierarchy without overwhelming the viewport.

## Layout & Spacing
The system employs a **Fixed Grid** model for the main content area with a maximum width of 1440px, centered on the screen. The layout is anchored by a persistent `280px` left sidebar.

Vertical rhythm is managed through a three-tier "Stack" system (8px, 16px, 32px). Gutters are fixed at 24px to ensure distinct separation between Bento-style metric cards. On mobile, the sidebar transitions to a hidden drawer, and page margins compress from 40px to 16px to maximize horizontal real estate for data tables.

## Elevation & Depth
Depth is established through **Tonal Layers** and **Ambient Shadows**. The base background is the `surface` color (`#f7f9fb`), while primary content containers (cards, tables) use pure white backgrounds to create a clear "lift."

**Shadows:** Elements like metric cards use a custom ultra-diffused shadow: `0px 4px 20px rgba(15, 23, 42, 0.05)`. This creates a soft, modern lift without the heaviness of traditional drop shadows. 

**Layering:** The sidebar and top app bar use subtle borders (`outline-variant`) rather than shadows to define boundaries, keeping the navigation feeling integrated and lightweight.

## Shapes
The shape language is **Soft** and professional. Standard UI components like buttons and input fields utilize a `0.25rem` (4px) base radius. Container elements like Bento cards and action panels use `0.5rem` (8px) to soften the large surface areas. Full rounding (pills) is reserved exclusively for notification badges and status tags.

## Components
- **Buttons:** Primary buttons are solid `secondary` blue with white text. Ghost buttons use an `outline-variant` border. All buttons use `label-md` typography.
- **Cards:** Bento-style cards feature a 1px border (`#e2e8f0`) and the custom ambient shadow. They should include internal padding of `stack-lg` (32px).
- **Chips/Badges:** Use `label-sm` font. Status-specific backgrounds (e.g., error-container) should have high contrast with their text for accessibility.
- **Inputs:** Search bars and text fields feature a 1px border and 40px height. Focus states should use a 2px `secondary` ring with 20% opacity.
- **Lists/Tables:** Use `divide-y` with a light slate color. Rows should feature a subtle hover state (`surface-container-low`) and a transition duration of 200ms.
- **Navigation:** Active sidebar items use a 4px left-border accent in the `secondary` color and a slightly lighter background fill to denote the current location.