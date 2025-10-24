import {AfterViewInit, Component, DestroyRef, inject, OnChanges, OnInit, SimpleChanges, ViewChild} from '@angular/core';
import {NgForOf, NgIf} from "@angular/common";
import {FormsModule, ReactiveFormsModule} from "@angular/forms";
import {ActivatedRoute, NavigationEnd, Router} from '@angular/router';
import {
  BoxMissingIconLargeComponent
} from '../../common/missing-icons/box/missing-icon-large/box-missing-icon-large.component';
import {
  RoundMissingIconLargeComponent
} from '../../common/missing-icons/round/round-missing-icon-large/round-missing-icon-large.component';
import {SearchComponent} from '../search/search.component';
import {AuthService} from '../../../services/auth/auth.service';
import { ToastrService } from '../../../services/toastr/toastr.service';
import {SearchService} from '../../../services/search/search.service';
import {SearchResult} from '../../../models/SearchResult';
import {MatProgressSpinner} from '@angular/material/progress-spinner';
import {filter, Subscription} from 'rxjs';
import {Album} from '../../../models/Album';
import {Song} from '../../../models/Song';
import {PlayerService} from '../../../services/player/player.service';
import {
  BoxMissingIconSmallComponent
} from '../../common/missing-icons/box/missing-icon-small/box-missing-icon-small.component';

@Component({
  selector: 'app-search-results-page',
  standalone: true,
  imports: [
    NgForOf,
    NgIf,
    ReactiveFormsModule,
    FormsModule,
    BoxMissingIconLargeComponent,
    RoundMissingIconLargeComponent,
    SearchComponent,
    MatProgressSpinner,
    BoxMissingIconSmallComponent
  ],
  templateUrl: './search-results.component.html',
  styleUrl: './search-results.component.scss'
})
export class SearchResultsComponent implements OnInit {
  router = inject(Router);
  route = inject(ActivatedRoute);
  toastr = inject(ToastrService);
  auth = inject(AuthService);
  searchService = inject(SearchService);
  routeSubscription: Subscription | undefined;
  playerService = inject(PlayerService);

  loading = true;
  searchResult: SearchResult = {albums: [], songs: [], artists: []};
  searchTerm: string = "";

  ngOnInit() {
    this.searchTerm = this.route.snapshot.params['query'];
    this.routeSubscription = this.route.paramMap.subscribe(params => {
      if (params.get('query')) {
        this.searchTerm = params.get('query')!;
      }
      this.search();
    });
  }

  search() {
    this.loading = true;
    this.searchService.search(this.searchTerm).subscribe({
      next: value => {
        this.searchResult = value;
        this.loading = false;
        setTimeout(() => this.applyHorizontalScrollBar(), 100);
      },
      error: err => {
        this.loading = false;
        this.toastr.error("Error", "Error querying: " + err);
      }
    })
  }

  getArtists(item: Album | Song) {
    return item.artists.map(a => a.name).join(" ")
  }

  applyHorizontalScrollBar() {
    const containers = document.querySelectorAll('.horizontal-scroller');

    containers.forEach(container => {
      container.addEventListener(
        'wheel',
        e => {
          e.preventDefault();
          (container as HTMLElement).scrollLeft += (e as WheelEvent).deltaY;
        },
        { passive: false }
      );
    });
  }
}
