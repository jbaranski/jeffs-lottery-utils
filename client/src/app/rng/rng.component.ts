import { Component } from '@angular/core';

interface Lottery {
  whiteBalls: number[];
  xupBall: number;
  evenOdd: [number, number];
  lowHigh: [number, number];
  consecutive: number;
}

@Component({
  selector: 'app-rng',
  imports: [],
  templateUrl: './rng.component.html',
  styleUrl: './rng.component.css'
})
export class RngComponent {
  NUMS: number = 3; // Number of random draws to generate
  megamillions: Lottery[] = [];
  powerballs: Lottery[] = [];

  ngOnInit(): void {
    // Mega Millions 1-70 white balls, 1-25 Mega Ball
    // Powerball 1-69 white balls, 1-26 Powerball
    for (let i = 0; i < this.NUMS; i++) {
      this.megamillions.push(this.lotteryRng(70, 25));
      this.powerballs.push(this.lotteryRng(69, 26));
    }
  }

  lotteryRng(max: number, xupMax: number): Lottery {
    while (true) {
      const candidate: number[] = this.candidateWhiteBalls(max);
      const candidateSet = new Set<number>(candidate);
      const consecutiveSeen = new Set<number>();
      let mid = Math.floor(max / 2);
      let even = 0;
      let low = 0;
      let consecutive = 0;
      for (let i = 0; i < candidate.length; i++) {
        const num = candidate[i];
        if (num % 2 == 0) {
          even += 1;
        }
        if (num <= mid) {
          low += 1;
        }
        if (!consecutiveSeen.has(num - 1) && candidateSet.has(num - 1)) {
          consecutive += 1;
          consecutiveSeen.add(num - 1);
          consecutiveSeen.add(num);
        }
        if (!consecutiveSeen.has(num + 1) && candidateSet.has(num + 1)) {
          consecutive += 1;
          consecutiveSeen.add(num + 1);
          consecutiveSeen.add(num);
        }
      }
      // If even,odd and low,high are both 4,1 imbalanced
      // If even,odd OR low,high are all one way or other
      // If consecutives > 1 (never got any consecutives to show up though so it may never appear in practice...)
      if (
        ((even == 4 || even == 1) && (low == 4 || low == 1)) ||
        even == 5 ||
        even == 0 ||
        low == 5 ||
        low == 0 ||
        consecutive > 1
      ) {
        continue;
      }
      return {
        whiteBalls: candidate,
        xupBall: this.generateRandomNumber(xupMax),
        evenOdd: [even, 5 - even],
        lowHigh: [low, 5 - low],
        consecutive: consecutive
      };
    }
  }

  candidateWhiteBalls(max: number): number[] {
    const nums: number[] = [];
    const seen = new Set<number>();
    while (nums.length < 5) {
      let num = this.generateRandomNumber(max);
      while (seen.has(num)) {
        num = this.generateRandomNumber(max);
      }
      nums.push(num);
      seen.add(num);
    }
    return nums.sort((a, b) => a - b);
  }

  generateRandomNumber(max: number): number {
    // Generate a random integer between 1 and x
    const min = 1;
    const cryptoRandom = crypto.getRandomValues(new Uint32Array(1))[0];
    return min + (cryptoRandom % (max - min + 1));
  }
}
