# codemap - app/src/screens/

## Responsibility
Screen components - full-page views for each app flow.

## Screens

| Screen | File | Purpose |
|--------|------|---------|
| Homepage | `home/HomepageScreen.tsx` | Landing page, routes to auth |
| Login | `auth/LoginScreen.tsx` | User authentication |
| Registration | `auth/RegistrationScreen.tsx` | User registration |
| User Panel | `dashboard/UserPanelScreen.tsx` | Logged-in home dashboard |
| Today | `today/TodayScreen.tsx` | Active plan tracking, meal checkoff |
| Plan List | `plans/PlanListScreen.tsx` | List all meal plans |
| Plan Detail | `plans/PlanDetailScreen.tsx` | Single plan details |
| Day Detail | `plans/DayDetailScreen.tsx` | Meals for specific day |
| Plan Creation | `create/PlanCreationScreen.tsx` | Create new meal plan wizard |
| Grocery List | `grocery/GroceryListScreen.tsx` | Generated grocery items |
| Pantry | `pantry/PantryScreen.tsx` | User pantry management |
| Settings | `settings/SettingsScreen.tsx` | User preferences |
| Change Password | `settings/ChangePasswordScreen.tsx` | Password update |
| About | `settings/AboutScreen.tsx` | App info |

## Navigation Structure
- Auth flows: `AuthNavigator` → Homepage → Login/Registration
- Main flows: `MainNavigator` (bottom tabs + stack) → All logged-in screens
