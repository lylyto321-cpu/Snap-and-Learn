import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.snapandlearn.hanyulearn',
  appName: 'Snap & Learn',
  webDir: 'www',
  android: {
    allowMixedContent: false,
    captureInput: true,
    webContentsDebuggingEnabled: false
  },
  plugins: {
    Camera: {
      saveToGallery: false
    }
  }
};

export default config;
