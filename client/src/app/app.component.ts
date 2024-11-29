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
  powerball: number[] = []
  powerup: number = 0;
  megamillions: number[] = []
  megaplier: number = 0;
  constructor(private http: HttpClient) {}

  async ngOnInit(): Promise<void> {
    const megamillions_history = await firstValueFrom(this.http.get('https://raw.githubusercontent.com/jbaranski/jeffs-lottery-utils/refs/heads/main/numbers/megamillions.json'));
    const powerball_history = await firstValueFrom(this.http.get('https://raw.githubusercontent.com/jbaranski/jeffs-lottery-utils/refs/heads/main/numbers/powerball.json'));
    this.generatePowerball();
  }

  generatePowerball(): void {
    this.megamillions = Array.from({ length: 5 }, (_1, _2) => this.generateRandomNumber(70));
    this.megaplier = this.generateRandomNumber(25);

    this.powerball = Array.from({ length: 5 }, (_1, _2) => this.generateRandomNumber(69));
    this.powerup = this.generateRandomNumber(26);
  }

  generateMegaMillions(): void {

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
