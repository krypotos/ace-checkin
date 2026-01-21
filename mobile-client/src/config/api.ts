// API Configuration
// Change this to your server URL when deploying

// For local development:
// - Android Emulator: use 10.0.2.2 (maps to host localhost)
// - iOS Simulator: use localhost
// - Real device: use your computer's local IP (e.g., 192.168.1.x)

import { Platform } from 'react-native';

const getBaseUrl = (): string => {
  // Check if we have an environment variable set
  // You can set this in app.json or via Expo's extra config

  if (__DEV__) {
    // Development mode
    if (Platform.OS === 'android') {
      // Android emulator uses 10.0.2.2 to reach host machine
    //   return 'http://10.0.2.2:8000';
    return 'http://192.168.68.105:8000';
    }
    // iOS simulator and web can use localhost
    return 'http://localhost:8000';
  }

  // Production - replace with your actual server URL
  return 'https://your-server.com';
};

export const API_CONFIG = {
  baseUrl: getBaseUrl(),
  timeout: 10000, // 10 seconds
  endpoints: {
    members: '/api/members',
    entry: '/api/entry',
    payment: '/api/payment',
    memberSummary: (id: number) => `/api/member/${id}/summary`,
  },
};

// Helper to build full URL
export const apiUrl = (path: string): string => {
  return `${API_CONFIG.baseUrl}${path}`;
};
