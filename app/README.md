# OptiMeal Mobile App

Mobile-first cross-platform application for OptiMeal meal planning optimization.

## Tech Stack

- **Framework**: React Native + Expo
- **Language**: TypeScript
- **Navigation**: React Navigation
- **State Management**: Zustand
- **API Client**: Axios
- **UI Library**: React Native Paper
- **Testing**: Jest + React Native Testing Library

## Project Structure

```
app/
├── src/
│   ├── components/       # Reusable UI components
│   ├── screens/          # Screen components
│   ├── navigation/       # Navigation configuration
│   ├── services/         # API clients and business logic
│   ├── context/          # React Context providers
│   ├── hooks/            # Custom React hooks
│   ├── theme/            # Theme configuration (SINGLE SOURCE OF TRUTH)
│   └── types/            # TypeScript type definitions
├── assets/               # Images, fonts, icons
├── __tests__/            # Test files
├── App.tsx               # Root component
├── app.json              # Expo configuration
├── package.json          # Dependencies
└── tsconfig.json         # TypeScript configuration
```

## Setup

### Prerequisites

- Node.js 18+ (LTS)
- npm or yarn
- Expo CLI (`npm install -g expo-cli`)
- iOS Simulator (Mac only) or Android Emulator

### Installation

1. **Install dependencies**:
   ```bash
   cd app
   npm install
   # or
   yarn install
   ```

2. **Set up environment variables**:
   - Copy `.env.example` to `.env.local`
   - Update `API_URL` to point to your backend (default: `http://localhost:8000/api/v1`)

3. **Start the development server**:
   ```bash
   npm start
   # or
   expo start
   ```

4. **Run on device/simulator**:
   - **iOS**: Press `i` in the terminal or scan QR code with Camera app
   - **Android**: Press `a` in the terminal or scan QR code with Expo Go app
   - **Web**: Press `w` in the terminal

## Development

### Running Tests

```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

### Type Checking

```bash
npm run type-check
```

### Linting

```bash
# Check code
npm run lint

# Auto-fix issues
npm run lint -- --fix
```

## Platform Support

- **iOS**: 13.0+
- **Android**: 8.0+ (API level 26)
- **Web**: Modern browsers (Chrome, Firefox, Safari, Edge)

## Features

### Core Features
- ✅ User authentication (register, login, logout)
- ✅ Meal plan creation with optimization
- ✅ Plan viewing with waste metrics
- ✅ Grocery list generation
- ✅ User settings (language, theme, units)

### Mobile-First Design
- Responsive layout scaling from mobile to tablet to web
- Touch-optimized UI components
- Smooth animations (60 fps target)
- Single source of truth for styling (`src/theme/`)

### Offline Support
- View cached meal plans offline
- Settings persisted locally
- Network status detection

## Theme System

The app uses a centralized theme system for consistent styling:

```typescript
// src/theme/
├── colors.ts      # Color palette (SINGLE SOURCE OF TRUTH)
├── spacing.ts     # Spacing constants
├── typography.ts  # Font styles
└── index.ts       # Exports complete theme
```

**Usage**:
```typescript
import { colors, spacing } from '@/theme';

const styles = StyleSheet.create({
  container: {
    backgroundColor: colors.background,
    padding: spacing.md,
  },
});
```

## API Integration

The app communicates with the FastAPI backend using Axios:

```typescript
// src/services/api.ts - Base Axios client
// src/services/authService.ts - Authentication
// src/services/planService.ts - Meal plans
// src/services/groceryService.ts - Grocery lists
```

API types are shared with the backend via `shared/types/api-contracts.ts`.

## Navigation

The app uses React Navigation with the following structure:

```
AppNavigator (Root)
├── AuthNavigator (Unauthenticated)
│   ├── Login
│   └── Registration
└── MainNavigator (Authenticated)
    ├── Home (Tab)
    ├── Plans (Tab)
    ├── Create Plan (Tab)
    └── Settings (Tab)
```

## State Management

- **Zustand**: Global state (meal plans, user data)
- **React Context**: Auth state, theme settings
- **Local Storage**: AsyncStorage for persistence

## Building for Production

### Android APK

```bash
expo build:android
```

### iOS IPA

```bash
expo build:ios
```

### Web Build

```bash
npm run web-build
# Output in web-build/
```

## Troubleshooting

### Metro Bundler Cache Issues

```bash
expo start -c
```

### Dependency Issues

```bash
rm -rf node_modules
npm install
```

### iOS Simulator Not Opening

```bash
expo ios --simulator="iPhone 15 Pro"
```

## Contributing

1. Follow mobile-first design principles
2. Ensure components are modular and reusable
3. Use the centralized theme system
4. Write tests for new features
5. Check TypeScript types (`npm run type-check`)

For detailed guidelines, see the project constitution: `../.specify/memory/constitution.md`

## License

Private project - All rights reserved.
