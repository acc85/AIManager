# AI Manager - Chat Desktop Design System

A specialized design system for high-fidelity AI chat interfaces within the Cognitive Enterprise ecosystem. It emphasizes deep navigation contrast, focused conversation threads, and persistent context.

## Visual Language

### Color Palette
- **Primary Sidebar**: `#0f172a` (Deep Slate) - Creates a strong anchor for navigation and system-level actions.
- **Surface**: `#f8fafc` (Off-White) - The main background for the conversation area, providing a clean and focused canvas.
- **Brand Action**: `#0052ff` (Vibrant Blue) - Used for primary CTAs like 'New Instance' and the message send button.
- **Message Bubbles**:
  - **User**: `#0052ff` with white text for high prominence.
  - **AI/System**: White with a subtle border for a distinct yet integrated feel.

### Typography
- **Font Family**: Hanken Grotesk
- **Hierarchy**:
  - **Page Title**: Semi-bold, large (e.g., 24px) for clear context.
  - **Message Text**: Regular, balanced line height (e.g., 16px) for comfortable reading.
  - **Metadata (Time/Model)**: Small, muted slate for secondary information.
  - **Monospace**: Used for code blocks or system-generated parameters (e.g., latency metrics).

### Component Styling
- **Roundness**: `ROUND_FOUR` (4px radius) for high-density elements like input fields and utility cards.
- **Message Bubbles**: Slightly more rounded (8px) to soften the conversational interface.
- **Elevation**: Flat design with very subtle shadows for buttons to maintain a modern, professional look.
- **Input Field**: Large, clean textarea with persistent utility actions (attachment, mic) and a clear primary action.

## Layout Patterns

### Workspace Structure
- **Persistent Left Sidebar**: Fixed width (approx. 280px) containing brand identity, main navigation tabs, a prominent 'New Instance' CTA, and user profile management.
- **Header Bar**: Displays current view title, model information (e.g., GPT-4 Pro), and global utilities like search and notifications.
- **Centered Conversation Thread**: Max-width container for chat messages to maintain readability on large displays.
- **Floating Action Deck**: A series of quick-action suggestion chips (Summarize, Check Logs, Security Audit) pinned below the message input for proactive AI engagement.
