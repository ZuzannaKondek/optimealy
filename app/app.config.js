export default {
  expo: {
    name: 'OptiMealy',
    slug: 'optimealy',
    version: '0.1.0',
    sdkVersion: '54.0.0',
    scheme: 'optimealy',
    orientation: 'portrait',
    userInterfaceStyle: 'automatic',
    // Explicitly disable Expo Router
    experiments: {
      typedRoutes: false,
    },
    splash: {
      resizeMode: 'contain',
      backgroundColor: '#4CAF50', // Primary green color
    },
    assetBundlePatterns: ['**/*'],
    ios: {
      supportsTablet: true,
      bundleIdentifier: 'com.optimealy.app',
    },
    android: {
      adaptiveIcon: {
        backgroundColor: '#4CAF50',
      },
      package: 'com.optimealy.app',
    },
    web: {
      // Metro web has been fragile with some deps using `import.meta`.
      // Webpack is more forgiving here.
      bundler: 'webpack',
    },
    extra: {
      apiUrl: process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
    },
    // Icon omitted until we add a real image asset.
  },
};
