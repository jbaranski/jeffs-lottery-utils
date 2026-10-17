---
name: jeff-skill-angular-aws-cognito
description: Integrate AWS Cognito authentication into a zoneless, signal-based Angular app using AWS Amplify v6 and the Cognito hosted UI — Amplify setup, auth service, functional guard, OAuth callback, and an interceptor that attaches the ID token to API calls. Use when adding login, sign-out, or route protection to an Angular app with AWS Cognito.
---

# Angular + AWS Cognito (Amplify v6, hosted UI)

Authentication uses Cognito User Pools through the **hosted UI** with the OAuth 2.0 authorization code flow (Amplify adds PKCE automatically). There is no embedded login form and no `@aws-amplify/ui-angular`.

The code below follows the Angular conventions in `jeff-skill-angular-project` and the Angular agents: standalone, zoneless, `inject()`, signals, lazy-loaded routes, Angular v20+ file naming (`sign-in.ts`, class `SignIn`).

## Contract with the backend

- API calls send the Cognito **ID token** (not the access token) in the `Authorization` header as the raw token string — **no `Bearer` prefix**. The API Gateway Cognito authorizer must be configured for ID tokens.
- The token is attached only to requests for `environment.api`, never to third-party URLs.

If the backend expects something else, change the interceptor, not every call site.

## Install

```bash
npm install aws-amplify
```

Use the latest v6 release.

## Configuration values

| Key                 | Value                                                                       |
| ------------------- | --------------------------------------------------------------------------- |
| User Pool ID        | `<USER_POOL_ID>`                                                            |
| User Pool Client ID | `<USER_POOL_CLIENT_ID>` (no secret)                                         |
| OAuth domain        | `<COGNITO_DOMAIN>` (e.g. `auth.example.com`)                                |
| Scopes              | `email`, `openid`                                                           |
| Redirect sign-in    | dev `http://localhost:4200/callback`, prod `https://<PROD_DOMAIN>/callback` |
| Redirect sign-out   | dev `http://localhost:4200`, prod `https://<PROD_DOMAIN>`                   |

Both redirect URLs for each environment must also be registered on the Cognito app client.

**`src/environments/environment.ts`** (and `environment.prod.ts` with the production URLs):

```typescript
export const environment = {
  api: 'https://<API_ID>.execute-api.<REGION>.amazonaws.com/<STAGE>',
  userPoolId: '<USER_POOL_ID>',
  userPoolClientId: '<USER_POOL_CLIENT_ID>',
  oauthDomain: '<COGNITO_DOMAIN>',
  oauthRedirectSignIn: 'http://localhost:4200/callback',
  oauthRedirectSignOut: 'http://localhost:4200'
};
```

These values are public client configuration, not secrets.

## Configure Amplify before bootstrap

**`src/main.ts`**

```typescript
import { bootstrapApplication } from '@angular/platform-browser';
import { Amplify } from 'aws-amplify';
import 'aws-amplify/auth/enable-oauth-listener'; // completes the code exchange when Cognito redirects back
import { App } from './app/app';
import { appConfig } from './app/app.config';
import { environment } from './environments/environment';

Amplify.configure({
  Auth: {
    Cognito: {
      userPoolId: environment.userPoolId,
      userPoolClientId: environment.userPoolClientId,
      signUpVerificationMethod: 'code',
      userAttributes: { email: { required: true } },
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

bootstrapApplication(App, appConfig).catch((err) => console.error(err));
```

## Auth service

**`src/app/auth/auth.service.ts`**

```typescript
import { Injectable, signal } from '@angular/core';
import { fetchAuthSession, signInWithRedirect, signOut } from 'aws-amplify/auth';

@Injectable({ providedIn: 'root' })
export class AuthService {
  readonly authenticated = signal(false);

  async isAuthenticated(): Promise<boolean> {
    const { tokens } = await fetchAuthSession();
    this.authenticated.set(tokens !== undefined);
    return this.authenticated();
  }

  async idToken(): Promise<string | undefined> {
    const { tokens } = await fetchAuthSession(); // refreshes expired tokens automatically
    return tokens?.idToken?.toString();
  }

  signIn(): Promise<void> {
    return signInWithRedirect();
  }

  async signOut(): Promise<void> {
    await signOut(); // redirects through the hosted UI to redirectSignOut
    this.authenticated.set(false);
  }
}
```

## Guard

**`src/app/auth/auth.guard.ts`**

```typescript
import { inject } from '@angular/core';
import { CanActivateFn } from '@angular/router';
import { AuthService } from './auth.service';

export const authGuard: CanActivateFn = async () => {
  const auth = inject(AuthService);
  if (await auth.isAuthenticated()) {
    return true;
  }
  await auth.signIn();
  return false;
};
```

## OAuth callback

Cognito redirects to `/callback?code=...`. Wait for Amplify's `signInWithRedirect` Hub event rather than assuming the exchange has already finished.

**`src/app/auth/callback.ts`**

```typescript
import { ChangeDetectionStrategy, Component, DestroyRef, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { Hub } from 'aws-amplify/utils';

@Component({
  selector: 'app-callback',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @if (error()) {
      <p>Sign-in failed. <a href="/">Return home</a></p>
    } @else {
      <p>Signing you in…</p>
    }
  `
})
export class Callback {
  readonly error = signal(false);

  constructor() {
    const router = inject(Router);
    const stop = Hub.listen('auth', ({ payload }) => {
      if (payload.event === 'signInWithRedirect') {
        void router.navigateByUrl('/dashboard');
      } else if (payload.event === 'signInWithRedirect_failure') {
        this.error.set(true);
      }
    });
    inject(DestroyRef).onDestroy(stop);
  }
}
```

A `/sign-in` route needs no component: protect a route with `authGuard` and link to it, or call `AuthService.signIn()` from a button.

## Routes

**`src/app/app.routes.ts`** — protected features are lazy-loaded; nothing from them is imported here.

```typescript
import { Routes } from '@angular/router';
import { authGuard } from './auth/auth.guard';

export const routes: Routes = [
  { path: '', loadComponent: () => import('./landing/landing').then((m) => m.Landing) },
  { path: 'callback', loadComponent: () => import('./auth/callback').then((m) => m.Callback) },
  {
    path: 'dashboard',
    canActivate: [authGuard],
    loadComponent: () => import('./dashboard/dashboard').then((m) => m.Dashboard)
  },
  { path: '**', redirectTo: '' }
];
```

Add `canActivate: [authGuard]` to every protected route.

## Attach the token to API calls

**`src/app/auth/auth.interceptor.ts`**

```typescript
import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { from, switchMap } from 'rxjs';
import { environment } from '../../environments/environment';
import { AuthService } from './auth.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  if (!req.url.startsWith(environment.api)) {
    return next(req);
  }
  const auth = inject(AuthService);
  return from(auth.idToken()).pipe(
    switchMap((token) => next(token ? req.clone({ setHeaders: { Authorization: token } }) : req))
  );
};
```

**`src/app/app.config.ts`**

```typescript
import { ApplicationConfig } from '@angular/core';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideRouter } from '@angular/router';
import { authInterceptor } from './auth/auth.interceptor';
import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [provideRouter(routes), provideHttpClient(withInterceptors([authInterceptor]))]
};
```

Components then call the API through services that use `HttpClient` and expose results as signals (`toSignal()` at the boundary) — no per-call token handling.

## Testing

- Mock `aws-amplify/auth` (`fetchAuthSession`, `signInWithRedirect`, `signOut`) with `vi.mock`; never hit Cognito from unit tests.
- Cover: guard allows with tokens and redirects without; interceptor adds the header only for `environment.api`; callback navigates on `signInWithRedirect` and shows the error state on failure.
