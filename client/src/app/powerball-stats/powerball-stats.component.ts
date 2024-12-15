import { Component } from '@angular/core';
import { Analysis, Statistic } from '../app.component';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

@Component({
  selector: 'app-powerball-stats',
  imports: [],
  templateUrl: './powerball-stats.component.html',
  styleUrl: './powerball-stats.component.css'
})
export class PowerballStatsComponent {
  evenOdd: Statistic[] = [];
  lowHigh: Statistic[] = [];
  consecutives: Statistic[] = [];
  evenOddlowHigh: Statistic[] = [];
  evenOddConsecutive: Statistic[] = [];
  lowHighConsecutive: Statistic[] = [];
  evenOddLowHighConsecutive: Statistic[] = [];
  updatedDate: string = '';
  totalDraws: number = 0;

  constructor(private http: HttpClient) {}

  async ngOnInit(): Promise<void> {
    const megamillionsAnalysis: Analysis = (await firstValueFrom(
      this.http.get(
        'https://raw.githubusercontent.com/jbaranski/jeffs-lottery-utils/refs/heads/main/numbers/powerball-analysis.json'
      )
    )) as Analysis;
    this.evenOdd = megamillionsAnalysis.white_balls.even_odd;
    this.lowHigh = megamillionsAnalysis.white_balls.low_high;
    this.consecutives = megamillionsAnalysis.white_balls.consecutive;
    this.evenOddlowHigh = megamillionsAnalysis.white_balls.even_odd_lo_hi;
    this.evenOddConsecutive = megamillionsAnalysis.white_balls.even_odd_consecutive;
    this.lowHighConsecutive = megamillionsAnalysis.white_balls.lo_hi_consecutive;
    this.evenOddLowHighConsecutive = megamillionsAnalysis.white_balls.even_odd_lo_hi_consecutive;
    this.updatedDate = megamillionsAnalysis.updated_date;
    this.totalDraws = megamillionsAnalysis.total_draws;
  }
}
