# Issue Backlog

This file tracks issues observed during development and testing.

---

## Issue #1 - Meal Plan Creation Progress Indicator Stuck
**Date Added:** 2025-01-27  
**Status:** Resolved
**Date Resolved:** 2026-01-13

**Description:**  
After "Create Meal Plan" is pressed, the "creating meal plan" icon keeps scrolling at 0% without raising. The progress indicator does not update during the meal plan creation process.

**Resolution:**
- Updated backend status endpoint to return 10% progress when status is "pending" (previously returned null/0%)
- Improved frontend polling to start immediately (500ms) instead of after 1 second
- Changed progress calculation to use 0 as fallback instead of 50
- Reduced polling interval to 1.5 seconds for faster status updates

---

## Issue #2 - No Redirect After Meal Plan Creation
**Date Added:** 2025-01-27  
**Status:** Resolved
**Date Resolved:** 2026-01-13

**Description:**  
After Create Meal Plan is completed, it does not redirect to the ready plan. Instead, it allows for creating a meal plan again and stays on the same page. The user should be redirected to view the newly created plan.

**Resolution:**
- Removed duplicate navigation logic from handleSubmit function (was causing conflicts)
- Improved useEffect redirect logic to properly handle completion state
- Added 500ms delay before resetting creation state to ensure navigation completes
- Added error handling to reset state after failed creation
- Fixed polling to properly detect completed status and trigger navigation

---

## Issue #3 - Day Details View Shows Duplicate Dish Types
**Date Added:** 2025-01-27  
**Status:** Resolved
**Date Resolved:** 2026-01-13

**Description:**  
The Day Details view displays multiple dishes of the same type. For example, it shows "Breakfast bagel with cream cheese", "breakfast", and "breakfast burrito" all as separate breakfast items, when they should likely be grouped or filtered.

**Resolution:**
- Updated MealCard component to prioritize course_type over meal_type for dish-based plans
- For dish-based plans, now always displays course_type (e.g., "BREAKFAST", "2ND BREAKFAST", "DINNER") 
- This ensures each dish is clearly differentiated by its course type
- Added isDishBasedPlan prop to MealCard to handle display logic appropriately
- Updated section title to show dish count for dish-based plans

---

## Issue #4 - Day Details View Missing Dish Quantity Information
**Date Added:** 2025-01-27  
**Status:** Resolved
**Date Resolved:** 2026-01-13

**Description:**  
The Day Details view does not display the amount of dishes which users required. The quantity/amount information for dishes is not shown in the view.

**Resolution:**
- Updated MealCard to display "1 dish" instead of "X servings" for dish-based plans
- Made dish weight display more prominent and always visible for dish-based plans
- Changed weight formatting to round to nearest gram for better readability
- Added clearer labels: "Dish weight: Xg" instead of just "Weight: Xg"
- Section header now shows total dish count for dish-based plans (e.g., "Dishes (5)")

---

## Issue #5 - Meal Plan Optimization Undershoots Calorie Target
**Date Added:** 2026-02-13  
**Status:** Open

**Description:**  
Optimization consistently falls short of the calorie target by approximately 10-20%. To actually reach ~2200 kcal, users must run the optimizer targeting 2600-2800 kcal, which then produces plans oscillating around 2200. The algorithm should produce plans close to the target when given 2200. It must be possible since higher targets find appropriate dishes. The macro constraints may be over-constraining the solution.

**Acceptance Criteria:**
- For a 2200 kcal target, plans should average within ~5% of 2200 kcal.
- No need to overshoot targets to reach desired calories.

---

## Issue #6 - Plans List Does Not Show Generated Plans
**Date Added:** 2026-02-13  
**Status:** Open

**Description:**  
After creating a plan, it does not appear in Active Plans nor Current Plans. Current functionality may only present the active plan. Users also need to see draft plans they were working on. "My Plans" should display all generated plans in a table—active, drafts, and outdated—so users can find and continue working on any plan they've created.

**Acceptance Criteria:**
- "My Plans" table shows all plans: active, draft, and outdated.
- Newly created plans appear in the list immediately.
- Draft plans are visible and selectable for continued editing.