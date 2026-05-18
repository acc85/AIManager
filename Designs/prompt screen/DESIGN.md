---
name: Cognitive Enterprise
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
  secondary: '#0058be'
  on-secondary: '#ffffff'
  secondary-container: '#2170e4'
  on-secondary-container: '#fefcff'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#0b1c30'
  on-tertiary-container: '#75859d'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dae2fd'
  primary-fixed-dim: '#bec6e0'
  on-primary-fixed: '#131b2e'
  on-primary-fixed-variant: '#3f465c'
  secondary-fixed: '#d8e2ff'
  secondary-fixed-dim: '#adc6ff'
  on-secondary-fixed: '#001a42'
  on-secondary-fixed-variant: '#004395'
  tertiary-fixed: '#d3e4fe'
  tertiary-fixed-dim: '#b7c8e1'
  on-tertiary-fixed: '#0b1c30'
  on-tertiary-fixed-variant: '#38485d'
  background: '#f7f9fb'
  on-background: '#191c1e'
  surface-variant: '#e0e3e5'
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
  sidebar-width: 280px
  sidebar-collapsed: 72px
  container-max: 1440px
  gutter: 24px
  margin-page: 40px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 32px
---

## Brand & Style
This design system is engineered for high-density, mission-critical desktop environments where artificial intelligence meets enterprise workflows. The brand personality is **authoritative, precise, and unobtrusive**, ensuring that complex data remains the focal point while the interface provides a calm, structured scaffolding.

The design style is **Corporate Modern with a Technical Edge**. It prioritizes clarity through generous whitespace, a strict adherence to a systematic grid, and subtle interactive cues that suggest intelligence without visual noise. The goal is to evoke a sense of "quiet power"—a tool that is incredibly capable but stays out of the user's way until needed.

## Colors
The palette is rooted in a professional **Deep Blue and Slate Gray** spectrum. 

- **Primary (#0F172A):** Used for the sidebar, high-level navigation, and primary text to establish a strong hierarchical anchor.
- **Secondary (#3B82F6):** An energetic "Electric Blue" reserved for primary actions, active states, and AI-driven insights.
- **Tertiary (#64748B):** A muted slate used for secondary text, icons, and non-essential UI decorators.
- **Neutral (#F8FAFC):** A clean, cool-toned background color that reduces eye strain during long-form desktop usage.

Surface colors utilize a tiered "Slate" system:
- `surface-main`: #FFFFFF (Cards and workspace)
- `surface-muted`: #F1F5F9 (Backgrounds and inactive states)
- `surface-dark`: #0F172A (Sidebar and dark-mode elements)

## Typography
Typography is optimized for long-term legibility and data density on large displays. 

- **Hanken Grotesk** provides a modern, sharp look for headlines, giving the interface a professional yet contemporary feel.
- **Inter** is the workhorse for all body copy and UI elements, chosen for its exceptional readability at small sizes and high x-height.
- **JetBrains Mono** is utilized sparingly for metadata, labels, and AI-generated code snippets or data points, emphasizing the technical nature of the application.

For desktop layouts, prioritize `body-md` (16px) as the standard reading size to prevent eye fatigue, using `body-sm` only for secondary metadata or sidebar links.

## Layout & Spacing
The layout follows a **Hybrid Sidebar-Grid Model**. The primary navigation is anchored to a vertical sidebar on the left, which can be collapsed to an icon-only view to maximize workspace.

1.  **Main Content Area:** Uses a 12-column fluid grid with a maximum width of 1440px to prevent line lengths from becoming unreadable on ultra-wide monitors.
2.  **Rhythm:** An 8px base unit governs all spatial relationships. 
3.  **Sidebar:** Fixed at 280px for standard navigation, utilizing a "Deep Blue" background to separate intent (navigation) from action (content).
4.  **Margins:** A generous 40px outer margin ensures the content feels breathable, while internal card padding is strictly set to 24px for consistency.

## Elevation & Depth
The design system employs **Tonal Layering** with subtle **Ambient Shadows** to define hierarchy. 

- **Level 0 (Background):** The base `neutral` gray (#F8FAFC). No shadow.
- **Level 1 (Cards/Workspace):** Pure white (#FFFFFF) with a very soft, diffused shadow (0px 4px 20px rgba(15, 23, 42, 0.05)). This is the primary surface for data.
- **Level 2 (Dropdowns/Modals):** Pure white with a more defined shadow (0px 10px 30px rgba(15, 23, 42, 0.12)) to lift the element above the workspace.
- **Separators:** Use 1px borders in `slate-200` (#E2E8F0) instead of shadows for internal divisions within a card to maintain a flat, technical aesthetic.

## Shapes
The shape language is **Soft and Professional**. A standard radius of 4px (`rounded-sm` or `0.25rem`) is applied to most UI components like buttons, input fields, and tags. This creates a precise, engineered feel. 

Large containers and cards use a slightly more pronounced 8px (`rounded-lg`) radius to soften the overall layout. Avoid pill-shaped buttons except for specialized "AI Suggestion" chips to distinguish them from standard system actions.

## Components
- **Buttons:** Primary buttons use the `Secondary` blue with white text. Secondary buttons use a slate-outline style. Desktop buttons should have a minimum height of 40px for a substantial feel.
- **Sidebar Navigation:** Items feature a 4px active-state indicator on the left edge. Hover states use a subtle opacity shift (10%) of the primary color.
- **Input Fields:** Use a solid white background with a 1px `slate-300` border. On focus, the border transitions to `Secondary` blue with a subtle 2px outer glow.
- **Cards:** The foundational container. Always white, 8px corner radius, with a 24px internal padding. 
- **AI Data Chips:** Small, mono-spaced labels using `label-sm` typography, featuring a light blue tinted background (#EFF6FF) to highlight machine-processed data.
- **Data Tables:** High-density, no outer borders, using 1px horizontal dividers only. Header cells use `label-md` in uppercase for clear categorization.