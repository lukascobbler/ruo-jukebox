import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import {NgIf} from '@angular/common';
import {NavbarComponent} from './components/common/navbar/navbar.component';
import {SongNavbarComponent} from './components/common/song-navbar/song-navbar.component';
import {PlayerComponent} from './components/common/player/player.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, NgIf, NavbarComponent, SongNavbarComponent, PlayerComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'front-end';
}
