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
  sumDistribution: Statistic[] = [];
  powerballHotness: Statistic[] = [];
  updatedDate: string = '';
  totalDraws: number = 0;

  constructor(private http: HttpClient) {}

  async ngOnInit(): Promise<void> {
    const powerballAnalysis: Analysis = (await firstValueFrom(
      this.http.get(
        'https://raw.githubusercontent.com/jbaranski/jeffs-lottery-utils/refs/heads/main/numbers/powerball-analysis.json'
      )
    )) as Analysis;
    this.evenOdd = powerballAnalysis.white_balls.even_odd;
    this.lowHigh = powerballAnalysis.white_balls.low_high;
    this.consecutives = powerballAnalysis.white_balls.consecutive;
    this.sumDistribution = powerballAnalysis.white_balls.sum_distribution;
    this.evenOddlowHigh = powerballAnalysis.white_balls.even_odd_lo_hi;
    this.evenOddConsecutive = powerballAnalysis.white_balls.even_odd_consecutive;
    this.lowHighConsecutive = powerballAnalysis.white_balls.lo_hi_consecutive;
    this.evenOddLowHighConsecutive =
      powerballAnalysis.white_balls.even_odd_lo_hi_consecutive;
    this.powerballHotness = powerballAnalysis.red_ball_hotness!;
    this.updatedDate = powerballAnalysis.updated_date;
    this.totalDraws = powerballAnalysis.total_draws;
  }
}
