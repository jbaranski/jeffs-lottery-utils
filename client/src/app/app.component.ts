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
  powerballs: number[][] = [[]];
  powerup: number[] = [];
  megamillions: number[][] = [[]];
  megaplier: number[] = [];
  seen: Set<number> = new Set<number>();
  constructor(private http: HttpClient) {}

  async ngOnInit(): Promise<void> {
    // const megamillions_history = await firstValueFrom(this.http.get('https://raw.githubusercontent.com/jbaranski/jeffs-lottery-utils/refs/heads/main/numbers/megamillions.json'));
    // const powerball_history = await firstValueFrom(this.http.get('https://raw.githubusercontent.com/jbaranski/jeffs-lottery-utils/refs/heads/main/numbers/powerball.json'));
    this.megamillions = Array.from({ length: this.NUMS }, (_1, _2) => Array.from(this.unqiueRandomNumbers(70)));
    this.megaplier = Array.from({ length: this.NUMS }, (_1, _2) => this.generateRandomNumber(25));

    this.powerballs = Array.from({ length: this.NUMS }, (_1, _2) => Array.from(this.unqiueRandomNumbers(69)));
    this.powerup = Array.from({ length: this.NUMS }, (_1, _2) => this.generateRandomNumber(26));
  }

  unqiueRandomNumbers(max: number, size: number = 5): Set<number> {
    const uniqueNumbers = new Set<number>();
    while (uniqueNumbers.size < size) {
      const num = this.generateRandomNumber(max);
      if (this.seen.has(num)) {
        continue;
      }
      uniqueNumbers.add(num);
    }
    return uniqueNumbers;
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
