import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';
import { firstValueFrom } from 'rxjs';

interface Statistic {
  type: string
  pct: string
}

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


  constructor(private http: HttpClient) {}

  async ngOnInit(): Promise<void> {
    const megamillionsAnalysis: any = await firstValueFrom(this.http.get('https://raw.githubusercontent.com/jbaranski/jeffs-lottery-utils/refs/heads/main/numbers/megamillions-analysis.json'));
    this.evenOdd = megamillionsAnalysis.white_balls.even_odd;
    this.lowHigh = megamillionsAnalysis.white_balls.low_high;
    this.consecutives = megamillionsAnalysis.white_balls.consecutive;
    this.evenOddlowHigh = megamillionsAnalysis.white_balls.even_odd_lo_hi;
    this.evenOddConsecutive = megamillionsAnalysis.white_balls.even_odd_consecutive;
    this.lowHighConsecutive = megamillionsAnalysis.white_balls.lo_hi_consecutive;
    this.evenOddLowHighConsecutive = megamillionsAnalysis.white_balls.even_odd_lo_hi_consecutive;

  }
}
