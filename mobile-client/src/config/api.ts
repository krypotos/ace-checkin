// API Configuration
// Change this to your server URL when deploying

// For local development:
// - Android Emulator: use 10.0.2.2 (maps to host localhost)
// - iOS Simulator: use localhost
// - Real device: use your computer's local IP (e.g., 192.168.1.x)

import { Platform } from 'react-native';

// =============================================================
// PRODUCTION CONFIGURATION
// Update these values when deploying to your DigitalOcean droplet
// =============================================================
const PRODUCTION_URL = 'https://YOUR_DROPLET_IP_HERE';
const PRODUCTION_API_KEY = 'YOUR_API_KEY_HERE';

// Development API key (empty string skips auth in dev mode)
const DEV_API_KEY = '';

const getBaseUrl = (): string => {
  if (__DEV__) {
    // Development mode
    if (Platform.OS === 'android') {
      // Android emulator uses 10.0.2.2 to reach host machine
      // return 'http://10.0.2.2:8000';
      return 'http://192.168.68.105:8000';
    }
    // iOS simulator and web can use localhost
    return 'http://localhost:8000';
  }

  // Production - your DigitalOcean droplet
  return PRODUCTION_URL;
};

const getApiKey = (): string => {
  if (__DEV__) {
    return DEV_API_KEY;
  }
  return PRODUCTION_API_KEY;
};

export const API_CONFIG = {
  baseUrl: getBaseUrl(),
  apiKey: getApiKey(),
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
