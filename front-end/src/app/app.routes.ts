import { Routes } from '@angular/router';
import {HomeComponent} from './components/user/home/home.component';
import {GenresComponent} from './components/user/discovery/genres/genres.component';

export const routes: Routes = [
  {path: "home", component: HomeComponent},
  {path: "discovery", component: GenresComponent}
];
