import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

// Mega Millions 1-70 white balls, 1-25 Mega Ball
// Powerball 1-69 white balls, 1-26 Powerball

@Component({
  selector: 'app-landing-page',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './landing-page.component.html',
  styleUrl: './landing-page.component.css'
})
export class LandingPageComponent {
  NUMS: number = 3;
  megamillions: number[][] = [];
  megaplier: number[] = [];
  powerballs: number[][] = [];
  powerup: number[] = [];

  ngOnInit(): void {
    // TODO: add options to generate optimal numbers
    this.whiteBall(this.megamillions, 70, new Set<number>());
    this.xUpBall(this.megaplier, 25, new Set<number>());

    this.whiteBall(this.powerballs, 69, new Set<number>());
    this.xUpBall(this.powerup, 26, new Set<number>());
  }

  whiteBall(target: number[][], max: number, seen: Set<number>) {
    for (let i = 0; i < this.NUMS; i++) {
      const nums: number[] = [];
      for (let j = 0; j < 5; j++) {
        nums.push(this.uniqueRandomNumber(max, seen));
      }
      target.push(nums);
    }
  }

  xUpBall(target: number[], max: number, seen: Set<number>) {
    for (let i = 0; i < this.NUMS; i++) {
      target.push(this.uniqueRandomNumber(max, seen));
    }
  }

  uniqueRandomNumber(max: number, seen: Set<number>): number {
    let num = this.generateRandomNumber(max);
    while (seen.has(num)) {
      num = this.generateRandomNumber(max);
    }
    seen.add(num);
    return num;
  }

  generateRandomNumber(max: number): number {
    // Generate a random integer between 1 and x
    const min = 1;
    const cryptoRandom = crypto.getRandomValues(new Uint32Array(1))[0];
    return min + (cryptoRandom % (max - min + 1));
  }
}
