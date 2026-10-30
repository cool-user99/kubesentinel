import { HttpClient } from '@angular/common/http';
import { Component, inject, OnInit, signal } from '@angular/core';

interface Item {
  id: number;
  name: string;
  created_at: string;
}

@Component({
  selector: 'app-root',
  template: `
    <main>
      <h1>KubeSentinel</h1>
      <p>
        API :
        <strong [class]="apiReady() ? 'ok' : 'ko'">
          {{ apiReady() ? 'prête' : 'indisponible' }}
        </strong>
      </p>

      <form (submit)="add($event, name)">
        <input #name placeholder="Nouvel item" maxlength="100" required />
        <button type="submit">Ajouter</button>
      </form>
      @if (error()) {
        <p class="ko">{{ error() }}</p>
      }

      <ul>
        @for (item of items(); track item.id) {
          <li>#{{ item.id }} — {{ item.name }}</li>
        } @empty {
          <li>Aucun item pour l'instant.</li>
        }
      </ul>
    </main>
  `,
  styles: `
    main { font-family: system-ui, sans-serif; max-width: 40rem; margin: 2rem auto; padding: 0 1rem; }
    .ok { color: #15803d; }
    .ko { color: #b91c1c; }
    form { display: flex; gap: .5rem; }
    input { flex: 1; padding: .4rem; }
  `,
})
export class App implements OnInit {
  private readonly http = inject(HttpClient);
  protected readonly items = signal<Item[]>([]);
  protected readonly apiReady = signal(false);
  protected readonly error = signal('');

  ngOnInit(): void {
    this.refresh();
  }

  // Chemins relatifs : l'Ingress route /api vers l'API, / vers ce frontend.
  refresh(): void {
    this.http.get<Item[]>('/api/items').subscribe({
      next: (items) => {
        this.items.set(items);
        this.apiReady.set(true);
      },
      error: () => {
        this.items.set([]);
        this.apiReady.set(false);
      },
    });
  }

  add(event: Event, input: HTMLInputElement): void {
    event.preventDefault();
    this.http.post('/api/items', { name: input.value }).subscribe({
      next: () => {
        input.value = '';
        this.error.set('');
        this.refresh();
      },
      error: () => this.error.set("Impossible d'ajouter l'item."),
    });
  }
}
