import Constants from 'expo-constants';

const ENV = {
  development: {
    apiUrl: 'http://192.168.6.77:8000',  // Your local network IP
    // apiUrl: 'http://localhost:8000', // Web
    // apiUrl: 'http://10.0.2.2:8000', // Android Emulator
    // apiUrl: 'http://YOUR_LOCAL_IP:8000', // Physical device (replace YOUR_LOCAL_IP with your computer's IP)
  },
  production: {
    apiUrl: 'http://192.168.6.77:8000',  // Update this when you deploy to production
  }
};

const getEnvVars = (env = Constants.expoConfig?.releaseChannel) => {
  if (__DEV__) {
    return ENV.development;
  }
  return ENV.production;
};

export default getEnvVars();
