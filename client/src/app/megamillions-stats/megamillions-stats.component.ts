import { Component, ChangeDetectionStrategy, computed, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { Analysis, Statistic } from '../app.component';
import { HttpClient } from '@angular/common/http';

const NO_STATS: Statistic[] = [];

@Component({
  selector: 'app-megamillions-stats',
  imports: [],
  templateUrl: './megamillions-stats.component.html',
  changeDetection: ChangeDetectionStrategy.Eager,
  styleUrl: './megamillions-stats.component.css'
})
export class MegamillionsStatsComponent {
  private readonly http = inject(HttpClient);

  private readonly analysis = toSignal(
    this.http.get<Analysis>(
      'https://raw.githubusercontent.com/jbaranski/jeffs-lottery-utils/refs/heads/main/numbers/megamillions-analysis.json'
    )
  );

  readonly evenOdd = computed(() => this.analysis()?.white_balls.even_odd ?? NO_STATS);
  readonly lowHigh = computed(() => this.analysis()?.white_balls.low_high ?? NO_STATS);
  readonly consecutives = computed(() => this.analysis()?.white_balls.consecutive ?? NO_STATS);
  readonly sumDistribution = computed(() => this.analysis()?.white_balls.sum_distribution ?? NO_STATS);
  readonly evenOddlowHigh = computed(() => this.analysis()?.white_balls.even_odd_lo_hi ?? NO_STATS);
  readonly evenOddConsecutive = computed(() => this.analysis()?.white_balls.even_odd_consecutive ?? NO_STATS);
  readonly lowHighConsecutive = computed(() => this.analysis()?.white_balls.lo_hi_consecutive ?? NO_STATS);
  readonly evenOddLowHighConsecutive = computed(
    () => this.analysis()?.white_balls.even_odd_lo_hi_consecutive ?? NO_STATS
  );
  readonly megamillionsHotness = computed(() => this.analysis()?.yellow_ball_hotness ?? NO_STATS);
  readonly updatedDate = computed(() => this.analysis()?.updated_date ?? '');
  readonly totalDraws = computed(() => this.analysis()?.total_draws ?? 0);
}
