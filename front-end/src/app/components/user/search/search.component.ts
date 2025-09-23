import {Component, inject, Input} from '@angular/core';
import {MatFormField, MatSuffix} from "@angular/material/form-field";
import {MatInput} from "@angular/material/input";
import {FormsModule, ReactiveFormsModule} from "@angular/forms";
import {Router} from '@angular/router';

@Component({
  selector: 'app-search',
  standalone: true,
  imports: [
    MatFormField,
    MatInput,
    MatSuffix,
    ReactiveFormsModule,
    FormsModule
  ],
  templateUrl: './search.component.html',
  styleUrl: './search.component.scss'
})
export class SearchComponent {
  router = inject(Router);

  @Input() searchTerm: string = "";

  search() {
    this.router.navigate(['search', this.searchTerm]);
  }
}
