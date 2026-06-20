import { Component, ChangeDetectionStrategy } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-landing-page',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './landing-page.component.html',
  changeDetection: ChangeDetectionStrategy.Eager,
  styleUrl: './landing-page.component.css'
})
export class LandingPageComponent {}
