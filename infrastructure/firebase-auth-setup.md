# Firebase Configuration for API Gateway

## Setup Instructions

### 1. Create Firebase Project
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login

# Initialize Firebase in your project
firebase init
```

### 2. Enable Authentication
1. Go to Firebase Console: https://console.firebase.google.com
2. Select your project
3. Navigate to Authentication > Sign-in method
4. Enable desired providers (Email/Password, Google, etc.)

### 3. Get Firebase Config
From Firebase Console, get your configuration:
```javascript
const firebaseConfig = {
  apiKey: "YOUR-API-KEY",
  authDomain: "YOUR-PROJECT.firebaseapp.com",
  projectId: "YOUR-PROJECT-ID",
  storageBucket: "YOUR-PROJECT.appspot.com",
  messagingSenderId: "YOUR-SENDER-ID",
  appId: "YOUR-APP-ID"
};
```

### 4. Update API Gateway Config
Replace in `api-gateway-config.yaml`:
- `YOUR-FIREBASE-PROJECT-ID` with your Firebase project ID
- `https://project-*-HASH-uc.a.run.app` with actual Cloud Run URLs

### 5. Deploy API Gateway
```bash
# Create API Gateway
gcloud api-gateway api-configs create lean-hub-config \
  --api=lean-hub-api \
  --openapi-spec=infrastructure/api-gateway-config.yaml \
  --project=YOUR-PROJECT-ID \
  --backend-auth-service-account=YOUR-SERVICE-ACCOUNT@YOUR-PROJECT-ID.iam.gserviceaccount.com

# Create gateway
gcloud api-gateway gateways create lean-hub-gateway \
  --api=lean-hub-api \
  --api-config=lean-hub-config \
  --location=us-central1 \
  --project=YOUR-PROJECT-ID
```

## Client Integration

### JavaScript/TypeScript Client
```typescript
import { initializeApp } from 'firebase/app';
import { getAuth, signInWithEmailAndPassword } from 'firebase/auth';

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// Login and get token
const userCredential = await signInWithEmailAndPassword(auth, email, password);
const token = await userCredential.user.getIdToken();

// Make authenticated request
const response = await fetch('https://hub.yourdomain.com/p1', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

### Python Client
```python
import requests
import firebase_admin
from firebase_admin import auth

# Get token
custom_token = auth.create_custom_token(uid)

# Make authenticated request
headers = {'Authorization': f'Bearer {custom_token}'}
response = requests.get('https://hub.yourdomain.com/p1', headers=headers)
```

## Security Benefits

1. **Single Entry Point**: All requests go through Firebase Auth
2. **Internal Services**: Cloud Run services are internal-only
3. **Zero Egress Costs**: Internal routing within GCP
4. **Centralized Auth**: Manage all authentication in one place
5. **Audit Logging**: Track all API access through Gateway logs
