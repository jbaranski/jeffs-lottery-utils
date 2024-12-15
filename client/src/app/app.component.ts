import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { firstValueFrom } from 'rxjs';

// Mega Millions 1-70 white balls, 1-25 Mega Ball
// Powerball 1-69 white balls, 1-26 Powerball

export interface Statistic {
  type: string
  pct: string
}

export interface Analysis {
  updated_date: string
  total_draws: number
  white_balls: WhiteBallsStats
}

export interface WhiteBallsStats {
  even_odd: Statistic[];
  low_high: Statistic[];
  consecutive: Statistic[];
  even_odd_lo_hi: Statistic[];
  even_odd_consecutive: Statistic[];
  lo_hi_consecutive: Statistic[];
  even_odd_lo_hi_consecutive: Statistic[];
}

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  NUMS: number = 3;
  megamillions: number[][] = [];
  megaplier: number[] = [];
  powerballs: number[][] = [];
  powerup: number[] = [];
  // TODO: add types
  evenOdd: any;
  lowHigh: any;
  consecutives: any;
  powerballEvenOdd: any;
  powerballLowHigh: any;
  powerballConsecutives: any;

  constructor(private http: HttpClient) {}

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

  ngAfterViewInit(): void {}

  ngOnDestroy(): void {}
}
