import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MegamillionsStatsComponent } from './megamillions-stats.component';

describe('MegamillionsStatsComponent', () => {
  let component: MegamillionsStatsComponent;
  let fixture: ComponentFixture<MegamillionsStatsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MegamillionsStatsComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(MegamillionsStatsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
