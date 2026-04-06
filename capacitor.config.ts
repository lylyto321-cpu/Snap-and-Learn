import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.snapandlearn.hanyulearn',
  appName: 'Snap & Learn',
  webDir: 'www',
  backgroundColor: '#F0F5F4',
  android: {
    allowMixedContent: false,
    captureInput: true,
    webContentsDebuggingEnabled: true
  },
  plugins: {
    Camera: {
      saveToGallery: false
    },
    CapacitorHttp: {
      enabled: true
    },
    GoogleAuth: {
      scopes: ['profile', 'email'],
      serverClientId: '26569546633-gesopkcgj3j7oqvo26075gtckftnbdce.apps.googleusercontent.com',
      forceCodeForRefreshToken: true
    }
  }
};

export default config;
