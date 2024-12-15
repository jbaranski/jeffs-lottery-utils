import { Routes } from '@angular/router';
import { LandingPageComponent } from './landing-page/landing-page.component';
import { MegamillionsStatsComponent } from './megamillions-stats/megamillions-stats.component';
import { PowerballStatsComponent } from './powerball-stats/powerball-stats.component';
import { RngComponent } from './rng/rng.component';

export const routes: Routes = [
  {
    path: '',
    component: LandingPageComponent
  },
  {
    path: 'rng',
    component: RngComponent
  },
  {
    path: 'megamillions-stats',
    component: MegamillionsStatsComponent
  },
  {
    path: 'powerball-stats',
    component: PowerballStatsComponent
  },
  {
    path: '**',
    redirectTo: '/',
    pathMatch: 'full'
  }
];
