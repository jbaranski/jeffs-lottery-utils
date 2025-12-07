import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { firstValueFrom } from 'rxjs';

export interface Statistic {
  type: string;
  pct: string;
}

export interface Analysis {
  updated_date: string;
  total_draws: number;
  white_balls: WhiteBallsStats;
  red_ball_hotness?: Statistic[];
  yellow_ball_hotness?: Statistic[];
}

export interface WhiteBallsStats {
  even_odd: Statistic[];
  low_high: Statistic[];
  consecutive: Statistic[];
  sum_distribution: Statistic[];
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
export class AppComponent {}
