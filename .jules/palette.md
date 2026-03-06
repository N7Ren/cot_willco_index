## 2026-03-06 - Interactive Table Headers Need Full Accessibility Support
**Learning:** Adding an `onclick` handler to an element like `<th>` makes it functional for mouse users, but it remains completely inaccessible to keyboard users and screen readers unless it also receives `tabindex="0"`, `role="button"`, an `onkeydown` handler for Enter/Space, and visible focus styles.
**Action:** When making custom non-interactive elements interactive, always implement the full suite of keyboard accessibility attributes (tabindex, role, keyboard handlers, and focus-visible styling).
