import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';
import { firstValueFrom } from 'rxjs';
import { Analysis, Statistic } from '../app.component';

@Component({
  selector: 'app-megamillions-stats',
  imports: [],
  templateUrl: './megamillions-stats.component.html',
  styleUrl: './megamillions-stats.component.css'
})
export class MegamillionsStatsComponent {
  evenOdd: Statistic[] = [];
  lowHigh: Statistic[] = [];
  consecutives: Statistic[] = [];
  evenOddlowHigh: Statistic[] = [];
  evenOddConsecutive: Statistic[] = [];
  lowHighConsecutive: Statistic[] = [];
  evenOddLowHighConsecutive: Statistic[] = [];
  sumDistribution: Statistic[] = [];
  megamillionsHotness: Statistic[] = [];
  updatedDate: string = '';
  totalDraws: number = 0;

  constructor(private http: HttpClient) {}

  async ngOnInit(): Promise<void> {
    const megamillionsAnalysis: Analysis = (await firstValueFrom(
      this.http.get(
        'https://raw.githubusercontent.com/jbaranski/jeffs-lottery-utils/refs/heads/main/numbers/megamillions-analysis.json'
      )
    )) as Analysis;
    this.evenOdd = megamillionsAnalysis.white_balls.even_odd;
    this.lowHigh = megamillionsAnalysis.white_balls.low_high;
    this.consecutives = megamillionsAnalysis.white_balls.consecutive;
    this.sumDistribution = megamillionsAnalysis.white_balls.sum_distribution;
    this.evenOddlowHigh = megamillionsAnalysis.white_balls.even_odd_lo_hi;
    this.evenOddConsecutive =
      megamillionsAnalysis.white_balls.even_odd_consecutive;
    this.lowHighConsecutive = megamillionsAnalysis.white_balls.lo_hi_consecutive;
    this.evenOddLowHighConsecutive =
      megamillionsAnalysis.white_balls.even_odd_lo_hi_consecutive;
    this.megamillionsHotness = megamillionsAnalysis.yellow_ball_hotness!;
    this.updatedDate = megamillionsAnalysis.updated_date;
    this.totalDraws = megamillionsAnalysis.total_draws;
  }
}
