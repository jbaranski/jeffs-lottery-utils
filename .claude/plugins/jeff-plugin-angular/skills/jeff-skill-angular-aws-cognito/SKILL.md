---
name: jeff-skill-angular-aws-cognito
description: Integrate AWS Cognito authentication into an Angular app using AWS Amplify v6. Implement an auth guard, auth service, and use the Cognito hosted UI for login. Use when setting up authentication for an Angular project with AWS Cognito, or when asked to "add login" or "integrate AWS Cognito" in an Angular app.
---

# Auth Guard, Auth Service & AWS Cognito Integration

## Overview

**AWS Amplify v6** with **Cognito User Pools** for authentication via **OAuth 2.0 authorization code flow**. There is no embedded login
form — all authentication goes through the Cognito hosted UI.

---

## Dependencies

**`package.json`**

```json
{
  "dependencies": {
    "aws-amplify": "^6.8.0"
  }
}
```

No `@aws-amplify/ui-angular`. The Cognito hosted UI is used exclusively.

---

## AWS Cognito Configuration Values

| Key                    | Value                                             |
| ---------------------- | ------------------------------------------------- |
| Region                 | `<YOUR_AWS_REGION>` (e.g. `us-east-1`)            |
| User Pool ID           | `<YOUR_USER_POOL_ID>`                             |
| User Pool Client ID    | `<YOUR_USER_POOL_CLIENT_ID>`                      |
| OAuth Domain           | `<YOUR_COGNITO_DOMAIN>` (e.g. `auth.example.com`) |
| OAuth Scopes           | `email`, `openid`                                 |
| Response Type          | `code` (authorization code flow)                  |
| Sign-up Verification   | Code-based                                        |
| Required User Attr     | Email                                             |
| Dev Redirect Sign-In   | `http://localhost:4200/callback`                  |
| Dev Redirect Sign-Out  | `http://localhost:4200`                           |
| Prod Redirect Sign-In  | `https://<YOUR_PROD_DOMAIN>/callback`             |
| Prod Redirect Sign-Out | `https://<YOUR_PROD_DOMAIN>`                      |

---

## Environment Files

**`src/environments/environment.ts`** (development)

```typescript
export const environment = {
  api: 'https://<YOUR_API_GATEWAY_ID>.execute-api.<REGION>.amazonaws.com/<STAGE>',
  userPoolId: '<YOUR_USER_POOL_ID>',
  userPoolClientId: '<YOUR_USER_POOL_CLIENT_ID>',
  oauthDomain: '<YOUR_COGNITO_DOMAIN>',
  oauthRedirectSignIn: 'http://localhost:4200/callback',
  oauthRedirectSignOut: 'http://localhost:4200'
};
```

**`src/environments/environment.prod.ts`** (production)

```typescript
export const environment = {
  api: 'https://<YOUR_API_GATEWAY_ID>.execute-api.<REGION>.amazonaws.com/<STAGE>',
  userPoolId: '<YOUR_USER_POOL_ID>',
  userPoolClientId: '<YOUR_USER_POOL_CLIENT_ID>',
  oauthDomain: '<YOUR_COGNITO_DOMAIN>',
  oauthRedirectSignIn: 'https://<YOUR_PROD_DOMAIN>/callback',
  oauthRedirectSignOut: 'https://<YOUR_PROD_DOMAIN>'
};
```

---

## Amplify Initialization

Amplify is configured once in `AppComponent.ngOnInit()` — **not** in `main.ts` or `app.config.ts`.

**`src/app/app.component.ts`**

```typescript
import { Component, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { Amplify } from 'aws-amplify';
import { environment } from '../environments/environment';
import { NgxSpinnerModule } from 'ngx-spinner';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive, NgxSpinnerModule],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  ngOnInit(): void {
    Amplify.configure({
      Auth: {
        Cognito: {
          userPoolId: environment.userPoolId,
          userPoolClientId: environment.userPoolClientId,
          signUpVerificationMethod: 'code',
          userAttributes: {
            email: { required: true }
          },
          loginWith: {
            oauth: {
              domain: environment.oauthDomain,
              scopes: ['email', 'openid'],
              redirectSignIn: [environment.oauthRedirectSignIn],
              redirectSignOut: [environment.oauthRedirectSignOut],
              responseType: 'code'
            }
          }
        }
      }
    });
  }
}
```

---

## Auth Service

**`src/app/auth.service.ts`**

```typescript
import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { fetchAuthSession, signInWithRedirect } from 'aws-amplify/auth';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  constructor(private router: Router) {}

  async isAuthenticated(): Promise<boolean> {
    const session = await fetchAuthSession();
    return session?.tokens !== undefined;
  }

  async redirectLogin(): Promise<void> {
    await signInWithRedirect();
  }

  async redirectHomeOrLogin(): Promise<void> {
    if (await this.isAuthenticated()) {
      this.router.navigate(['/dashboard']);
    } else {
      this.redirectLogin();
    }
  }
}
```

- `isAuthenticated()` — calls `fetchAuthSession()` and checks for presence of `tokens`
- `redirectLogin()` — calls `signInWithRedirect()` which redirects to the Cognito hosted UI
- `redirectHomeOrLogin()` — used by both `SignInComponent` and `AuthCallbackComponent` to route the user after auth state is determined

---

## Auth Guard

**`src/app/auth.guard.ts`**

```typescript
import { inject } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivateFn, RouterStateSnapshot } from '@angular/router';
import { AuthService } from './auth.service';

export const authGuard: CanActivateFn = async (route: ActivatedRouteSnapshot, state: RouterStateSnapshot) => {
  const authService = inject(AuthService);

  if (!(await authService.isAuthenticated())) {
    authService.redirectLogin();
    return false;
  }

  return true;
};
```

- Functional guard (`CanActivateFn`), not a class-based guard
- Uses `inject()` for DI (Angular 14+ pattern)
- Applied to all protected routes (e.g. `/dashboard`, `/feature`)

---

## Sign-In Component

**`src/app/sign-in/sign-in.component.ts`**

```typescript
import { Component } from '@angular/core';
import { AuthService } from '../auth.service';

@Component({
  selector: 'app-sign-in',
  imports: [],
  templateUrl: './sign-in.component.html',
  styleUrl: './sign-in.component.css'
})
export class SignInComponent {
  constructor(private authService: AuthService) {}

  async ngOnInit(): Promise<void> {
    await this.authService.redirectHomeOrLogin();
  }
}
```

- No UI — immediately redirects on `ngOnInit`
- If already authenticated, goes to `/dashboard`; otherwise triggers Cognito OAuth redirect

---

## Auth Callback Component

**`src/app/auth-callback/auth-callback.component.ts`**

```typescript
import { Component } from '@angular/core';
import { AuthService } from '../auth.service';

@Component({
  selector: 'app-auth-callback',
  imports: [],
  templateUrl: './auth-callback.component.html',
  styleUrl: './auth-callback.component.css'
})
export class AuthCallbackComponent {
  constructor(private authService: AuthService) {}

  async ngOnInit(): Promise<void> {
    await this.authService.redirectHomeOrLogin();
  }
}
```

- Handles the `/callback` route — the OAuth return URL from Cognito
- Amplify automatically exchanges the `?code=...` query param for tokens before component logic runs
- Calls `redirectHomeOrLogin()` to route the user to `/dashboard`

---

## Routing

**`src/app/app.routes.ts`**

```typescript
import { Routes } from '@angular/router';
import { LandingPageComponent } from './landing-page/landing-page.component';
import { SignInComponent } from './sign-in/sign-in.component';
import { AuthCallbackComponent } from './auth-callback/auth-callback.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { FeatureOneComponent } from './feature-one/feature-one.component';
import { StaticPageComponent } from './static-page/static-page.component';
import { authGuard } from './auth.guard';

export const routes: Routes = [
  { path: '', component: LandingPageComponent },
  { path: 'sign-in', component: SignInComponent },
  { path: 'callback', component: AuthCallbackComponent },
  { path: 'static-page', component: StaticPageComponent },
  { path: 'dashboard', component: DashboardComponent, canActivate: [authGuard] },
  { path: 'feature', component: FeatureOneComponent, canActivate: [authGuard] },
  { path: '**', redirectTo: '/', pathMatch: 'full' }
];
```

| Route          | Protected       | Purpose                                   |
| -------------- | --------------- | ----------------------------------------- |
| `/`            | No              | Landing page                              |
| `/sign-in`     | No              | Triggers OAuth redirect                   |
| `/callback`    | No              | OAuth return URL (Cognito redirects here) |
| `/static-page` | No              | Example unprotected static page           |
| `/dashboard`   | Yes (authGuard) | Post-login home / main feature            |
| `/feature`     | Yes (authGuard) | Any additional protected route            |

Add `canActivate: [authGuard]` to every protected route. Unprotected routes require no guard.

---

## Application Config

**`src/app/app.config.ts`**

```typescript
import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { routes } from './app.routes';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideAnimations } from '@angular/platform-browser/animations';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideHttpClient(withInterceptors([])),
    provideAnimations()
  ]
};
```

- Standalone application config (no NgModule)
- No auth-specific HTTP interceptor — token attachment is done manually per-request

---

## Token Usage in API Calls

There is **no auth HTTP interceptor**. Every component that calls the API manually
fetches the session and attaches the Cognito **ID token** as an `Authorization` header.

```typescript
import { fetchAuthSession } from 'aws-amplify/auth';
import { environment } from '../../environments/environment';

// Inside any async method that calls the API:
const session = await fetchAuthSession();
this.http.get(`${environment.api}/some-endpoint`, {
  headers: {
    Authorization: session.tokens?.idToken?.toString() || ''
  }
}).subscribe({ ... });
```

- Token type: **ID token** (not access token)
- Header name: `Authorization`
- No `Bearer ` prefix — raw token string
- Fallback: empty string `''` if token is undefined
- All HTTP verbs (GET, POST, PUT, DELETE) follow this same pattern

---

## HTTP Interceptor (spinner only — not auth-related)

If the project includes a loading spinner, a functional interceptor handles show/hide around HTTP requests. This is **not** related to auth.

**`src/app/spinner.interceptor.ts`**

```typescript
import { HttpErrorResponse, HttpEventType, HttpHandlerFn, HttpInterceptorFn, HttpRequest } from '@angular/common/http';
import { inject } from '@angular/core';
import { NgxSpinnerService } from 'ngx-spinner';
import { catchError, tap, throwError } from 'rxjs';

export const spinnerInterceptor: HttpInterceptorFn = (req: HttpRequest<unknown>, next: HttpHandlerFn) => {
  const spinner = inject(NgxSpinnerService);
  spinner.show();
  return next(req).pipe(
    tap((event) => {
      if (event.type === HttpEventType.Response) {
        spinner.hide();
      }
    }),
    catchError((error: HttpErrorResponse) => {
      spinner.hide();
      return throwError(() => error);
    })
  );
};
```

- Functional interceptor (`HttpInterceptorFn`)
- Handles loading spinner only — does **not** attach auth tokens

---

## Bootstrap

**`src/main.ts`**

```typescript
import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';

bootstrapApplication(AppComponent, appConfig).catch((err) => console.error(err));
```

`Amplify.configure()` runs inside `AppComponent.ngOnInit()` — after bootstrap, not before.

---

## End-to-End Authentication Flow

```
1. User visits /sign-in
   └── SignInComponent.ngOnInit()
       └── authService.redirectHomeOrLogin()
           ├── isAuthenticated() → false
           └── signInWithRedirect()
               └── browser redirects to Cognito hosted UI:
                   https://<YOUR_COGNITO_DOMAIN>/login
                   ?client_id=<YOUR_USER_POOL_CLIENT_ID>
                   &redirect_uri=<REDIRECT_SIGN_IN_URL>
                   &response_type=code
                   &scope=email+openid

2. User authenticates on Cognito hosted UI

3. Cognito redirects to /callback?code=AUTH_CODE
   └── Amplify SDK automatically exchanges the code for tokens
   └── AuthCallbackComponent.ngOnInit()
       └── authService.redirectHomeOrLogin()
           ├── isAuthenticated() → true (tokens now in Amplify session)
           └── router.navigate(['/dashboard'])

4. User navigates to a protected route (e.g. /dashboard, /feature)
   └── authGuard runs (NOTE: has bug — missing await, always passes)
       └── returns true

5. Any authenticated API call
   └── fetchAuthSession() → session.tokens.idToken
   └── HTTP request with header: Authorization: <raw idToken string>
```

---

## Notable Implementation Details

1. **No logout** — `signOut()` is not implemented; add it to `AuthService` if required
2. **No token refresh logic** — Amplify handles refresh automatically inside `fetchAuthSession()`
3. **Auth guard bug** — `authGuard` calls `authService.isAuthenticated()` without `await`; the guard always returns `true` regardless of auth state
4. **Amplify configured in component** — `Amplify.configure()` is in `AppComponent.ngOnInit()` rather than in `main.ts` before bootstrap; this works but is atypical
5. **ID token, not access token** — API calls use `idToken`; the backend (API Gateway) must be configured to validate Cognito ID tokens
6. **No PKCE config** — Amplify v6 handles PKCE automatically for `responseType: 'code'`
7. **No `Bearer` prefix** — the `Authorization` header is the raw token string, not `Bearer <token>`; the backend must match this expectation

## Integration with Other Skills

- **jeff-skill-angular-project**: Angular test creation and standards reference
