# Design System Specification: The Kinetic Hearth

## 1. Overview & Creative North Star

This design system is built to move beyond the utility of a "smart canteen" and into the realm of a high-end digital concierge. Our **Creative North Star is "The Kinetic Hearth."** It represents the intersection of futuristic precision (Kinetic) and the visceral, welcoming warmth of high-quality nourishment (Hearth).

We break the "standard template" look by rejecting rigid grids in favor of **intentional asymmetry** and **tonal depth**. The UI is treated not as a flat screen, but as a three-dimensional space where glass-like surfaces float over deep, infinite voids. We use exaggerated typography scales to create an editorial feel, ensuring that every data point feels like a curated piece of content rather than a row in a database.

---

## 2. Colors & Surface Philosophy

The color palette is rooted in a deep-space obsidian background, punctuated by high-chroma "flavor" accents that mimic glowing embers and fresh ingredients.

### The "No-Line" Rule
Standard UI relies on 1px borders to separate content. In this system, **solid borders are strictly prohibited.** Boundaries must be defined through:
- **Tonal Shifts:** Placing a `surface-container-high` element against a `surface` background.
- **Vignettes:** Using soft, radial gradients to draw the eye to the center of a container.
- **Negative Space:** Using the Spacing Scale to let elements breathe and find their own edges.

### Surface Hierarchy & Nesting
Think of the UI as physical layers of smoked glass.
- **Level 0 (Foundation):** `surface-container-lowest` (#000000) for global backgrounds.
- **Level 1 (Canvas):** `surface` (#0e0e0e) for primary content sections.
- **Level 2 (Objects):** `surface-container-high` (#20201f) for cards and interactive components.
- **Level 3 (Interactive):** `surface-container-highest` (#262626) for hovered states or active overlays.

### The "Glass & Gradient" Rule
To achieve the "Premium Startup" aesthetic, any floating element (Modals, Navigation Bars, Tooltips) must use **Glassmorphism**:
- **Fill:** `surface-variant` (#262626) at 60% opacity.
- **Effect:** Backdrop Blur (20px to 40px).
- **Signature Gradient:** Main CTAs must use a linear gradient from `primary` (#ffa84f) to `primary-container` (#fe9400) at a 135-degree angle to simulate the glow of a heat lamp.

---

## 3. Typography

Our typography is a dialogue between the bold, geometric authority of **Plus Jakarta Sans** and the refined, technical clarity of **Manrope**.

- **Display & Headlines (Plus Jakarta Sans):** These are the "hero" elements. Use `display-lg` for impactful statements. The tight tracking and bold weights convey speed and intelligence.
- **Body & Titles (Manrope):** Used for all functional reading. Manrope provides a humanistic touch that balances the "futuristic" tone with warmth.
- **Hierarchy as Identity:** We use high-contrast sizing. A `display-lg` headline should often sit adjacent to a `label-md` metadata point. This "Big/Small" relationship creates an editorial rhythm that feels like a premium magazine.

---

## 4. Elevation & Depth

We eschew traditional "Drop Shadows" for **Tonal Layering** and **Ambient Glows.**

### The Layering Principle
Depth is achieved by "stacking." A `surface-container-low` card placed on a `surface` background creates a natural, soft lift. This mimics how light interacts with physical objects in a dark room.

### Ambient Shadows
When an element must "float" (e.g., a 3D food model or a primary FAB):
- **Color:** Use a tinted shadow based on `primary` or `on-surface`.
- **Properties:** Extra-diffused (Blur: 40px - 80px) and low-opacity (4%-8%). It should feel like an atmospheric glow, not a dark smudge.

### The "Ghost Border" Fallback
If accessibility requires a container edge:
- **Rule:** Use the `outline-variant` (#484847) at **10-15% opacity**. It should be felt, not seen.

### Glassmorphism & Depth
By using backdrop blurs on `surface-variant` containers, we allow the vibrant `primary` and `secondary` accents to bleed through from the layers below, creating a sense of "Living UI."

---

## 5. Components

### Buttons
- **Primary:** Rounded `full`. Gradient fill (`primary` to `primary-container`). White text (`on-primary`). No border.
- **Secondary:** Rounded `xl`. Glassmorphism fill (`surface-variant` @ 40% + Blur). `outline-variant` Ghost Border.
- **Tertiary:** No fill. `primary` text. High-letter spacing `label-md` for a technical feel.

### Input Fields
- **Style:** `surface-container-low` fill. Bottom-only "Ghost Border" using `outline-variant` @ 20%.
- **Focus State:** The border transitions to a 2px `primary` gradient. The label floats and shrinks to `label-sm`.

### Cards & Lists
- **Rule:** **No Divider Lines.** 
- **Separation:** Use 24px - 32px of vertical padding.
- **Interactive Cards:** On hover, the background shifts from `surface-container-high` to `surface-bright`.

### Smart Canteen Contextuals (Specialty Components)
- **The "Nutrition Ring":** A circular progress indicator using `secondary` (#fecb00) and `tertiary` (#81ecff) to show caloric and macro-nutrient data.
- **The "Heat Map" Chip:** Small, `sm` rounded chips that use `error` (#ff7351) to indicate high-demand items or fast-selling meals.
- **3D Hero Plate:** Floating 3D assets should be positioned with `z-index` priority, casting an ambient `primary_dim` glow onto the `surface` below it.

---

## 6. Do's and Don'ts

### Do:
- **Embrace Asymmetry:** Let text elements align to a different vertical axis than images to create visual tension.
- **Use "Food-Inspired" Motion:** Transitions should be fluid and "organic"—think of the way honey pours or steam rises.
- **Prioritize Breathing Room:** If a layout feels crowded, increase the spacing. Luxury is defined by wasted space.

### Don't:
- **Never use 100% Opaque Borders:** This kills the premium "glassy" atmosphere.
- **Don't use Pure Grey:** Always ensure your "greys" are tinted with the deep obsidian tones of `surface` (#0e0e0e).
- **Avoid Default Shadows:** Never use the standard (0, 4, 10, 0.25) black shadow. It looks cheap and "out of the box."
- **No Sharp Corners:** Stick strictly to the `lg` (1rem) and `xl` (1.5rem) roundedness scale to maintain the "Soft Minimalist" feel.