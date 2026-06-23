# How to Build a Flutter App with Firebase Auth and Firestore

Most mobile apps need the same foundation: sign in with Google or Apple, persist user data in the cloud, and react to auth state across screens. Flutter plus Firebase covers all three without maintaining separate native auth SDKs for iOS and Android.

This is a deep-dive setup guide — from `flutter create` through Google Sign-In, Sign in with Apple, Cloud Firestore, Riverpod state, and GoRouter auth redirects. No product pitch; just the engineering path to a working mobile app skeleton you can extend.

## Table of contents

1. [Why Flutter + Firebase](#why-flutter--firebase)
2. [Prerequisites](#prerequisites)
3. [Create the Flutter project](#create-the-flutter-project)
4. [Firebase Console setup](#firebase-console-setup)
5. [Wire Firebase with FlutterFire CLI](#wire-firebase-with-flutterfire-cli)
6. [Dependencies](#dependencies)
7. [Initialize Firebase in main.dart](#initialize-firebase-in-maindart)
8. [Android platform config](#android-platform-config)
9. [iOS platform config](#ios-platform-config)
10. [Google Sign-In implementation](#google-sign-in-implementation)
11. [Apple Sign-In implementation](#apple-sign-in-implementation)
12. [Email/password auth](#emailpassword-auth)
13. [Auth repository and error handling](#auth-repository-and-error-handling)
14. [Riverpod providers for Firebase](#riverpod-providers-for-firebase)
15. [GoRouter auth-gated routing](#gorouter-auth-gated-routing)
16. [Firestore data model](#firestore-data-model)
17. [Security rules](#security-rules)
18. [Models: fromFirestore and toFirestore](#models-fromfirestore-and-tofirestore)
19. [Repository pattern with real-time streams](#repository-pattern-with-real-time-streams)
20. [Batch writes and atomic updates](#batch-writes-and-atomic-updates)
21. [Post-auth profile stub](#post-auth-profile-stub)
22. [Sign out](#sign-out)
23. [Platform differences (web, Android, iOS)](#platform-differences-web-android-ios)
24. [Common errors and fixes](#common-errors-and-fixes)
25. [Production checklist](#production-checklist)
26. [FAQ](#faq)

## Why Flutter + Firebase

| Layer | Flutter | Firebase |
|-------|---------|----------|
| UI | Single Dart codebase for iOS, Android, web | — |
| Auth | `firebase_auth` + platform sign-in packages | Google, Apple, email providers |
| Database | `cloud_firestore` streams into widgets | Real-time NoSQL, offline cache |
| Files | `firebase_storage` | Object storage for avatars, uploads |
| Config | `flutterfire configure` generates per-platform keys | One project, many apps |

Flutter removes duplicate Swift/Kotlin UI work. Firebase removes running your own auth server and sync layer. Together they get you to a signed-in user with live cloud data in days, not weeks.

## Prerequisites

- Flutter SDK 3.11+ (`flutter doctor` clean on iOS and Android toolchains)
- Xcode (for iOS simulator and Apple Sign-In capability)
- Android Studio or command-line Android SDK
- A Firebase project (free Spark tier is enough to start)
- Apple Developer account (required for Sign in with Apple on real devices)
- Node.js (for FlutterFire CLI via `dart pub global activate flutterfire_cli`)

## Create the Flutter project

```bash
flutter create my_app
cd my_app
flutter pub get
```

Use a reverse-DNS bundle ID from day one — you will register the same ID in Firebase, Apple Developer, and Google Cloud:

```bash
# Example — pick your own domain
# iOS: com.example.myapp
# Android: com.example.myapp
```

Organize `lib/` by feature early:

```
lib/
├── main.dart
├── app.dart
├── firebase_options.dart      # generated; gitignore in prod
├── core/
│   ├── router/app_router.dart
│   └── constants/google_auth_config.dart
├── data/
│   ├── models/
│   ├── repositories/
│   └── providers/
└── features/
    └── auth/
        ├── auth_repository.dart
        └── presentation/
```

## Firebase Console setup

1. Go to [Firebase Console](https://console.firebase.google.com/) → **Add project**.
2. Register apps for **iOS**, **Android**, and optionally **Web** with your bundle ID / package name.
3. Open **Build → Authentication → Sign-in method** and enable:
   - **Email/Password**
   - **Google**
   - **Apple** (requires Apple Services ID configuration — see iOS section)
4. Open **Build → Firestore Database** → create database in **production mode** (you will add rules immediately).
5. Note your **Project ID** — you need it for FlutterFire CLI.

## Wire Firebase with FlutterFire CLI

Install and run from the project root:

```bash
dart pub global activate flutterfire_cli
flutterfire configure --project=YOUR_PROJECT_ID
```

Select the platforms you target (iOS, Android, web, macOS). The CLI generates:

| File | Purpose |
|------|---------|
| `lib/firebase_options.dart` | `FirebaseOptions` per platform |
| `android/app/google-services.json` | Android Firebase config |
| `ios/Runner/GoogleService-Info.plist` | iOS Firebase config |
| `firebase.json` | Maps Flutter apps to Firebase |

**Gitignore** the generated secrets in team repos; commit a `firebase_options.dart.example` with placeholder keys for new developers:

```bash
cp lib/firebase_options.dart lib/firebase_options.dart.example
# Replace real keys in .example with YOUR_* placeholders
```

New clones run `flutterfire configure` locally to regenerate real files.

## Dependencies

Add to `pubspec.yaml`:

```yaml
dependencies:
  flutter:
    sdk: flutter
  firebase_core: ^3.13.0
  firebase_auth: ^5.5.3
  cloud_firestore: ^5.6.7
  firebase_storage: ^12.4.4
  google_sign_in: ^6.3.0
  sign_in_with_apple: ^8.0.0
  crypto: ^3.0.7
  flutter_riverpod: ^2.6.1
  go_router: ^15.1.2
  shared_preferences: ^2.5.3
```

| Package | Role |
|---------|------|
| `firebase_core` | Bootstrap all Firebase SDKs |
| `firebase_auth` | Auth state, credentials, sign-out |
| `cloud_firestore` | Real-time document database |
| `google_sign_in` | Native Google account picker → Firebase credential |
| `sign_in_with_apple` | Apple ID credential → Firebase OAuth |
| `crypto` | SHA-256 nonce for Apple Sign-In (required by Firebase) |
| `flutter_riverpod` | Dependency injection + reactive auth/data providers |
| `go_router` | Declarative routing with auth redirects |

Run `flutter pub get` after editing.

## Initialize Firebase in main.dart

Firebase must initialize **before** `runApp`. Wrap the app in `ProviderScope` for Riverpod:

```dart
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:my_app/app.dart';
import 'package:my_app/firebase_options.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  runApp(
    const ProviderScope(
      child: MyApp(),
    ),
  );
}
```

`DefaultFirebaseOptions.currentPlatform` picks web, Android, iOS, or macOS options automatically — no manual `if (Platform.isIOS)` in `main.dart`.

## Android platform config

### google-services plugin

In `android/settings.gradle.kts` (or root `build.gradle` on older templates):

```kotlin
plugins {
    id("com.google.gms.google-services") version "4.3.15" apply false
}
```

In `android/app/build.gradle.kts`:

```kotlin
plugins {
    id("com.android.application")
    id("com.google.gms.google-services")
    // ...
}

android {
    namespace = "com.example.myapp"
    defaultConfig {
        applicationId = "com.example.myapp"
    }
}
```

Place `google-services.json` in `android/app/` (FlutterFire generates it).

### SHA-1 fingerprint (critical for Google Sign-In)

Google Sign-In on Android fails with `ApiException: 10` / `DEVELOPER_ERROR` if Firebase does not know your signing certificate.

Debug keystore:

```bash
keytool -list -v -keystore ~/.android/debug.keystore -alias androiddebugkey -storepass android -keypass android
```

Copy the **SHA-1** into Firebase Console → Project settings → Your Android app → **Add fingerprint**.

For release builds, add the SHA-1 from your upload keystore too. Re-download `google-services.json` after adding fingerprints.

## iOS platform config

### Google Sign-In URL scheme

Open `ios/Runner/Info.plist` and add the **reversed client ID** from `GoogleService-Info.plist`:

```xml
<key>CFBundleURLTypes</key>
<array>
  <dict>
    <key>CFBundleURLSchemes</key>
    <array>
      <string>com.googleusercontent.apps.YOUR_IOS_CLIENT_NUM</string>
    </array>
  </dict>
</array>
<key>GIDClientID</key>
<string>YOUR_IOS_CLIENT_ID.apps.googleusercontent.com</string>
```

Without this, the Google account picker cannot return to your app.

### Sign in with Apple entitlement

In Xcode: **Runner target → Signing & Capabilities → + Capability → Sign in with Apple**.

This creates or updates `ios/Runner/Runner.entitlements`:

```xml
<key>com.apple.developer.applesignin</key>
<array>
  <string>Default</string>
</array>
```

In Firebase Console, configure Apple provider with your Apple Services ID, team ID, and key — follow Firebase's Apple setup wizard.

### Podfile

Firebase iOS pods often need static linking:

```ruby
target 'Runner' do
  use_frameworks! :linkage => :static
  flutter_install_all_ios_pods File.dirname(File.realpath(__FILE__))
end
```

Run `cd ios && pod install` after dependency changes.

## Google Sign-In implementation

Centralize OAuth client IDs in one file (extract from `GoogleService-Info.plist` and `google-services.json`):

```dart
class GoogleAuthConfig {
  static const iosClientId =
      'YOUR_IOS_CLIENT_ID.apps.googleusercontent.com';
  static const webClientId =
      'YOUR_WEB_CLIENT_ID.apps.googleusercontent.com';
}
```

The **web client ID** is used as `serverClientId` on mobile — it lets Firebase verify the ID token server-side. Find it in Firebase Console → Authentication → Google → Web SDK configuration, or as `client_type: 3` in `google-services.json`.

Auth repository method:

```dart
Future<void> signInWithGoogle() async {
  if (kIsWeb) {
    await _auth.signInWithPopup(GoogleAuthProvider());
    return;
  }

  final googleSignIn = GoogleSignIn(
    scopes: const ['email', 'profile'],
    clientId: defaultTargetPlatform == TargetPlatform.iOS
        ? GoogleAuthConfig.iosClientId
        : null,
    serverClientId: GoogleAuthConfig.webClientId,
  );

  try {
    await googleSignIn.signOut(); // clear stale session
  } catch (_) {}

  final account = await googleSignIn.signIn();
  if (account == null) {
    throw FirebaseAuthException(code: 'popup-closed-by-user');
  }

  final auth = await account.authentication;
  final credential = GoogleAuthProvider.credential(
    accessToken: auth.accessToken,
    idToken: auth.idToken,
  );
  await _auth.signInWithCredential(credential);
}
```

Key points:

- **iOS** needs explicit `clientId`.
- **Android** uses `serverClientId` only (plus SHA-1 in Console).
- **Web** uses `signInWithPopup` — no `google_sign_in` package flow.
- Sign out of Google before sign-in avoids stuck account picker states.

## Apple Sign-In implementation

Apple Sign-In is **iOS/macOS only** in most apps. Block it on Android and web with clear errors.

Firebase requires a **nonce**: generate a random string, pass SHA-256 of it to Apple, pass the raw nonce to Firebase:

```dart
import 'dart:convert';
import 'dart:math';
import 'package:crypto/crypto.dart';
import 'package:sign_in_with_apple/sign_in_with_apple.dart';

Future<void> signInWithApple() async {
  if (kIsWeb || defaultTargetPlatform == TargetPlatform.android) {
    throw FirebaseAuthException(
      code: 'operation-not-allowed',
      message: 'Apple sign-in is only supported on iOS and macOS.',
    );
  }

  final rawNonce = _generateNonce();
  final nonce = sha256.convert(utf8.encode(rawNonce)).toString();

  final appleCredential = await SignInWithApple.getAppleIDCredential(
    scopes: [
      AppleIDAuthorizationScopes.email,
      AppleIDAuthorizationScopes.fullName,
    ],
    nonce: nonce,
  );

  final idToken = appleCredential.identityToken;
  if (idToken == null) {
    throw FirebaseAuthException(code: 'invalid-credential');
  }

  final oauthCredential = OAuthProvider('apple.com').credential(
    idToken: idToken,
    rawNonce: rawNonce,
  );
  await _auth.signInWithCredential(oauthCredential);
}

String _generateNonce([int length = 32]) {
  const charset =
      '0123456789ABCDEFGHIJKLMNOPQRSTUVXYZabcdefghijklmnopqrstuvwxyz-._';
  final random = Random.secure();
  return List.generate(length, (_) => charset[random.nextInt(charset.length)])
      .join();
}
```

Show the Apple button only where supported:

```dart
bool get showAppleSignIn =>
    !kIsWeb && (Platform.isIOS || Platform.isMacOS);
```

Apple only sends the user's name **once** — capture it on first sign-in and write to Firestore immediately if you need display names.

## Email/password auth

Keep email as a fallback — required for reviewers and users without Google/Apple:

```dart
Future<void> signInWithEmail(String email, String password) async {
  await _auth.signInWithEmailAndPassword(email: email, password: password);
}

Future<void> signUpWithEmail(String email, String password) async {
  await _auth.createUserWithEmailAndPassword(email: email, password: password);
}
```

Password reset:

```dart
await FirebaseAuth.instance.sendPasswordResetEmail(email: email);
```

Enable **Email/Password** in Firebase Console or you get `operation-not-allowed`.

## Auth repository and error handling

Wrap Firebase exceptions into user-readable strings. Map the errors users actually hit:

| Code / symptom | User message |
|----------------|--------------|
| `ApiException: 10` / `developer_error` | Add Android SHA-1 in Firebase Console |
| `popup-closed-by-user` | Sign-in was cancelled |
| `email-already-in-use` | Try signing in instead |
| `account-exists-with-different-credential` | Email linked to another provider |
| Apple `AuthorizationErrorCode.canceled` | Sign-in was cancelled |
| `configuration-not-found` | Enable provider in Firebase Console |

A dedicated `authErrorMessage(Object error)` function keeps UI widgets thin — buttons catch errors and show SnackBars.

## Riverpod providers for Firebase

Register Firebase singletons once:

```dart
final firebaseAuthProvider = Provider<FirebaseAuth>(
  (ref) => FirebaseAuth.instance,
);

final firestoreProvider = Provider<FirebaseFirestore>(
  (ref) => FirebaseFirestore.instance,
);

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository(ref.watch(firebaseAuthProvider));
});

final authUidProvider = StreamProvider<String?>((ref) {
  return ref
      .watch(firebaseAuthProvider)
      .authStateChanges()
      .map((user) => user?.uid);
});

final currentUserIdProvider = Provider<String?>((ref) {
  return ref.watch(authUidProvider).valueOrNull;
});
```

`authStateChanges()` is the single source of truth for signed-in vs signed-out. Every Firestore provider gates on `currentUserIdProvider` — if UID is null, return `Stream.empty()` to avoid permission errors.

## GoRouter auth-gated routing

Do not call `context.go('/')` manually after sign-in. Let **GoRouter redirect** react to auth stream changes — otherwise you race navigation against Firestore profile creation.

```dart
const _publicAuthPaths = ['/welcome', '/sign-in', '/sign-up'];

final routerProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authUidProvider);
  final profileState = ref.watch(userProfileProvider);

  return GoRouter(
    initialLocation: '/welcome',
    redirect: (context, state) {
      final uid = authState.valueOrNull;
      final path = state.matchedLocation;

      if (authState.isLoading) return null;

      if (uid == null) {
        return _isPublicAuthPath(path) ? null : '/welcome';
      }

      final profile = profileState.valueOrNull;
      if (profileState.isLoading) return null;

      final target = routeAfterAuth(profile);

      if (_isPublicAuthPath(path)) {
        return path == target ? null : target;
      }

      if (target != '/') {
        final onSetup = path == target || path.startsWith('$target/');
        if (!onSetup) return target;
      }

      return null;
    },
    routes: [
      GoRoute(path: '/welcome', builder: (_, __) => const WelcomeScreen()),
      GoRoute(path: '/sign-in', builder: (_, __) => const SignInScreen()),
      // ... authenticated shell routes
    ],
  );
});
```

`routeAfterAuth(profile)` returns onboarding routes until required profile fields exist, then `/` for the main shell.

Pattern: **auth stream + profile stream → redirect function**. UI only triggers sign-in; routing follows state.

## Firestore data model

Use a **user-scoped hierarchy** — every document lives under the authenticated UID:

```
users/{uid}/profile/settings     ← single profile doc
users/{uid}/items/{itemId}       ← user-owned collection
users/{uid}/...
```

Centralize paths:

```dart
class FirestorePaths {
  static String userRoot(String uid) => 'users/$uid';
  static String profile(String uid) => '${userRoot(uid)}/profile/settings';
  static String items(String uid) => '${userRoot(uid)}/items';
}
```

Why subcollections under `users/{uid}`?

- Security rules are one line: `request.auth.uid == userId`
- Deletes are scoped — wipe `users/{uid}` subtree on account deletion
- No cross-user queries accidentally leaking data

Avoid flat top-level collections with a `userId` field until you need cross-user features — they complicate rules.

## Security rules

Deploy rules before shipping:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId}/{document=**} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

Test in Firebase Console **Rules playground** with simulated auth UID.

Never ship with `allow read, write: if true` except local emulators.

## Models: fromFirestore and toFirestore

Keep Firestore serialization on the model class:

```dart
class UserProfile {
  const UserProfile({
    required this.displayName,
    this.createdAt,
    this.onboardingComplete = false,
  });

  final String displayName;
  final DateTime? createdAt;
  final bool onboardingComplete;

  factory UserProfile.fromFirestore(
    DocumentSnapshot<Map<String, dynamic>> doc,
  ) {
    final data = doc.data() ?? {};
    return UserProfile(
      displayName: data['displayName'] as String? ?? '',
      createdAt: (data['createdAt'] as Timestamp?)?.toDate(),
      onboardingComplete: data['onboardingComplete'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toFirestore() {
    return {
      'displayName': displayName,
      'onboardingComplete': onboardingComplete,
      if (createdAt != null)
        'createdAt': Timestamp.fromDate(createdAt!),
    };
  }
}
```

Use `Timestamp` for dates in Firestore — not ISO strings — so queries and indexes work natively.

## Repository pattern with real-time streams

One repository per aggregate (profile, items, etc.):

```dart
class ProfileRepository {
  ProfileRepository(this._firestore);
  final FirebaseFirestore _firestore;

  DocumentReference<Map<String, dynamic>> _ref(String uid) =>
      _firestore.doc(FirestorePaths.profile(uid));

  Stream<UserProfile?> watch(String uid) {
    return _ref(uid).snapshots().map((snap) {
      if (!snap.exists) return null;
      return UserProfile.fromFirestore(snap);
    });
  }

  Future<void> save(String uid, UserProfile profile) async {
    await _ref(uid).set(profile.toFirestore(), SetOptions(merge: true));
  }
}
```

Wire into Riverpod:

```dart
final userProfileProvider = StreamProvider<UserProfile?>((ref) {
  final uid = ref.watch(currentUserIdProvider);
  if (uid == null) return const Stream.empty();
  return ref.watch(profileRepositoryProvider).watch(uid);
});
```

Widgets use `ref.watch(userProfileProvider)` — they rebuild automatically when Firestore pushes changes. No manual refresh buttons for sync.

## Batch writes and atomic updates

When two writes must succeed or fail together, use a batch:

```dart
final batch = _firestore.batch();
batch.set(itemRef, item.toFirestore());
batch.update(summaryRef, {'count': FieldValue.increment(1)});
await batch.commit();
```

`FieldValue.increment` is atomic — safe for counters and balances under concurrent writes.

Firestore batches cap at **500 operations** — paginate bulk deletes (400 docs per batch is a safe margin).

## Post-auth profile stub

After any sign-in, ensure a Firestore profile document exists before routing to the home screen:

```dart
Future<void> ensureAuthProfileStub(WidgetRef ref) async {
  final uid = ref.read(firebaseAuthProvider).currentUser?.uid;
  if (uid == null) return;

  final repo = ref.read(profileRepositoryProvider);
  final existing = await repo.get(uid);
  if (existing != null) return;

  final user = ref.read(firebaseAuthProvider).currentUser;
  await repo.save(
    uid,
    UserProfile(
      displayName: user?.displayName ?? '',
      createdAt: DateTime.now(),
    ),
  );
  ref.invalidate(userProfileProvider);
}
```

Call this from sign-in button handlers **after** `signInWithGoogle()` succeeds. Do not navigate manually — GoRouter redirect picks up the new profile stream.

For Google/Apple, pre-fill `displayName` from `FirebaseAuth.currentUser.displayName`.

## Sign out

Clear both Firebase **and** Google sessions:

```dart
Future<void> signOut() async {
  if (!kIsWeb) {
    await GoogleSignIn().signOut();
  }
  await _auth.signOut();
}
```

Missing Google sign-out causes the next sign-in to skip account picker and reuse the old Google account silently.

## Platform differences (web, Android, iOS)

| Feature | Web | Android | iOS |
|---------|-----|---------|-----|
| Google Sign-In | `signInWithPopup` | `google_sign_in` + SHA-1 | `google_sign_in` + URL scheme |
| Apple Sign-In | Not supported | Not supported | Native + entitlements |
| Email/password | Yes | Yes | Yes |
| Firestore offline | Limited | Yes | Yes |

Test all enabled providers on **real devices** — simulators miss Keychain, Google Play Services, and Apple ID edge cases.

## Common errors and fixes

### `ApiException: 10` (Google on Android)

**Cause:** SHA-1 not registered in Firebase Console, or wrong `google-services.json`.

**Fix:** Add debug and release SHA-1 fingerprints. Re-download json. Uninstall app. Reinstall.

### `invalid-credential` after Google Sign-In on iOS

**Cause:** Missing `GIDClientID` or URL scheme in `Info.plist`.

**Fix:** Copy values from `GoogleService-Info.plist`. Rebuild.

### Apple Sign-In `notHandled`

**Cause:** Sign in with Apple capability not enabled in Xcode.

**Fix:** Add capability, rebuild, verify entitlements file is linked in build settings.

### Firestore `permission-denied`

**Cause:** User not authenticated, wrong UID path, or rules not deployed.

**Fix:** Confirm `request.auth.uid` matches path. Deploy rules. Gate providers on non-null UID.

### GoRouter redirect loop

**Cause:** Redirect sends to `/welcome` while profile stream still loading.

**Fix:** Return `null` from redirect while `authState.isLoading` or `profileState.isLoading`.

## Production checklist

- [ ] Release keystore SHA-1 added to Firebase (Android)
- [ ] `GoogleService-Info.plist` and `google-services.json` from production Firebase apps
- [ ] Firestore rules deployed — no open reads
- [ ] Apple Sign-In enabled in Firebase + Apple Developer portal
- [ ] Auth error messages user-tested on device
- [ ] Profile stub creates doc on first sign-in
- [ ] Sign-out clears Google session
- [ ] `firebase_options.dart` gitignored; example file committed
- [ ] Firestore indexes created for compound queries (Console prompts automatically)

## FAQ

### Do I need a backend server?

Not for auth and CRUD. Firestore security rules enforce access. Add Cloud Functions when you need server secrets, webhooks, or trusted batch jobs.

### Riverpod vs Bloc vs Provider?

Any works. Riverpod pairs cleanly with `StreamProvider` for Firestore and auth streams. Pick one state layer and keep Firebase access in repositories — not in widgets.

### Can I use Supabase instead of Firestore?

Yes — auth and sync patterns differ. This guide targets Firebase because Google/Apple sign-in integration is first-class and offline cache is built in.

### How do I test without real Google/Apple accounts?

Use email/password auth in debug builds. Firebase Auth emulator suite supports local testing without hitting production.

### Should I put Firebase keys in `.env`?

FlutterFire embeds keys in `firebase_options.dart` — they are not secret on mobile (client-side). Security comes from **Firestore rules** and **App Check**, not hidden API keys.

## Related

- [SSE vs WebSocket vs REST API for Live AI](./sse-websocket-rest-api-compared.html)
- [How to Build a Production RAG Chatbot](./how-to-build-a-production-rag-chatbot.html)
