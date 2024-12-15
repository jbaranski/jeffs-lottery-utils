import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PowerballStatsComponent } from './powerball-stats.component';

describe('PowerballStatsComponent', () => {
  let component: PowerballStatsComponent;
  let fixture: ComponentFixture<PowerballStatsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PowerballStatsComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(PowerballStatsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
