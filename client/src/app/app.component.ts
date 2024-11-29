import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { firstValueFrom } from 'rxjs';

// Mega Millions 1-70 white balls, 1-25 Mega Ball
// Powerball 1-69 white balls, 1-26 Powerball

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
  constructor(private http: HttpClient) {}

  async ngOnInit(): Promise<void> {
    // const megamillions_history = await firstValueFrom(this.http.get('https://raw.githubusercontent.com/jbaranski/jeffs-lottery-utils/refs/heads/main/numbers/megamillions.json'));
    // const powerball_history = await firstValueFrom(this.http.get('https://raw.githubusercontent.com/jbaranski/jeffs-lottery-utils/refs/heads/main/numbers/powerball.json'));

    this.whiteBall(this.megamillions, 70, new Set<number>());
    this.xUp(this.megaplier, 25, new Set<number>());

    this.whiteBall(this.powerballs, 69, new Set<number>());
    this.xUp(this.powerup, 26, new Set<number>());
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

  xUp(target: number[], max: number, seen: Set<number>) {
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
