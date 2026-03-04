## 2024-03-03 - Added aria-current to active navigation links
**Learning:** Relying solely on color to indicate the active navigation state is inaccessible to screen readers and color-blind users.
**Action:** Always add aria-current="page" to active navigation links and provide a secondary visual indicator, such as an underline or border, for active states.## 2026-03-04 - Loading States for Long Sync Forms
**Learning:** Adding an immediate visual loading state (like disabling a submit button and showing a spinner) is crucial for synchronous form submissions that trigger long background tasks (like downloading 7 years of COT data). Without it, users may think the app is frozen and submit multiple times.
**Action:** When a form triggers a heavy backend operation without AJAX, use an `onsubmit` handler to immediately provide visual feedback and disable the submit button before the page unloads.
