---
name: Sentience Enterprise
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
  ai-accent: '#adc6ff'
  surface-border: '#e2e8f0'
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
  margin-page: 40px
  gutter: 24px
  stack-lg: 32px
  stack-md: 16px
  stack-sm: 8px
  sidebar-width: 280px
  container-max: 1440px
---

## Brand & Style

Sentience Enterprise is a design system tailored for high-stakes AI management and technical operations. The brand personality is **precise, authoritative, and sophisticated**, evoking the feel of a high-end command center. It targets technical leads and enterprise operators who require a balance between dense data visualization and clear, actionable insights.

The design style is **Corporate Modern with subtle Brutalist influences**. It utilizes a structured sidebar for navigation, a rigid grid for "Bento-style" metrics, and high-contrast primary areas to differentiate between system-generated insights and user-managed tasks. The aesthetic is clean and professional, prioritizing legibility and information density without sacrificing visual polish.

## Colors

The palette is anchored by **Deep Command Blue (#131b2e)**, used for structural navigation and high-priority containers to establish a sense of stability. **Action Blue (#0052ff)** serves as the primary functional color for buttons, progress indicators, and active states, ensuring clear affordance.

Neutral surfaces utilize a cool-toned grayscale starting with **Off-White (#f7f9fb)** for page backgrounds and pure white for elevated cards. Dark modes (where applicable) transition the primary container to a deeper tertiary navy. Semantic colors like urgent red and success green are used sparingly to signal system status and priority levels.

## Typography

The typography system uses a three-font strategy to balance character and utility:
- **Hanken Grotesk** is used for headlines and display metrics, providing a sharp, contemporary tech aesthetic.
- **Inter** handles all body copy and interface elements, ensuring maximum readability and a neutral, systematic feel.
- **JetBrains Mono** is reserved for metadata, labels, and system IDs, reinforcing the technical, developer-centric nature of the platform.

For mobile devices, `display-lg` should scale down to 36px/44px, and `headline-lg` should scale to 28px/36px to maintain hierarchy on smaller viewports.

## Layout & Spacing

The system follows a **Fixed Grid** approach for the main content area, maxing out at 1440px width and centered on the screen, while the navigation sidebar remains fixed to the left viewport edge. 

- **Sidebar:** 280px wide, providing a persistent anchor for navigation.
- **Bento Grid:** A flexible 4-column grid for metrics that collapses to 2 columns on tablets and 1 column on mobile.
- **Vertical Rhythm:** A base 8px unit drives the spacing system. Large sections are separated by 32px (`stack-lg`), while internal card elements use 16px (`stack-md`).
- **Responsive Behavior:** Below 1024px, the sidebar should collapse into a hamburger menu or a slim icon bar (72px) to prioritize content space.

## Elevation & Depth

Sentience Enterprise uses **Tonal Layers** supplemented by subtle **Ambient Shadows** to define its hierarchy.

- **Level 0 (Background):** The base page uses `#f7f9fb`, creating a neutral canvas.
- **Level 1 (Cards & Sidebar):** Primary content containers use white or primary-container navy. They are defined by a 1px border (`#e2e8f0`) and a very soft, diffused shadow (`0px 4px 20px rgba(15, 23, 42, 0.05)`).
- **Level 2 (Interactive):** Hover states on list items and buttons utilize a subtle shift in background color (e.g., `surface-container-low`) rather than increasing shadow depth, maintaining a flat, professional feel.
- **Level 3 (AI Insights):** Special AI-driven panels use a dark background with a 10% opacity icon pattern to signify a different "intelligence" layer within the UI.

## Shapes

The shape language is **Soft and Precise**. A base radius of 4px (`0.25rem`) is applied to standard buttons and inputs. Larger containers, such as dashboard cards and the sidebar navigation items, use 8px (`0.5rem`) to feel more modern and approachable. 

Status badges and tags use a "Semi-Pill" shape (fully rounded corners but rectangular proportions) to distinguish them from interactive buttons.

## Components

### Buttons
- **Primary:** Solid `#0052ff` with white text. 8px rounded corners.
- **Secondary/Outline:** 1px border with `#131b2e` text.
- **System:** Deep navy buttons for "Execute" or "New Instance" actions within primary-colored containers.

### Inputs
- Text inputs use a white background, 1px `#c6c6cd` border, and JetBrains Mono for placeholder text. Focused states should use a 2px Action Blue ring with 20% opacity.

### Chips & Badges
- Used for priority (URGENT, MEDIUM, LOW). These utilize low-saturation background tints of their semantic meaning (e.g., light red background for URGENT) with high-contrast text.

### Data Tables
- Header rows use `#f2f4f6` with uppercase `label-md` typography.
- Rows feature a subtle hover transition to `#eceef0`.
- Action icons (more_vert) are persistent but low-contrast until hovered.

### Cards (Bento)
- Cards are the primary container for metrics. They should include a `label-md` title, a `display-lg` value, and a footer area for trend indicators or progress bars.