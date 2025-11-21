import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-triage-search',
  templateUrl: './triage-search.component.html',
  styleUrls: ['./triage-search.component.css']
})
export class TriageSearchComponent {
  query = '';
  results: any[] = [];
  loading = false;

  constructor(private http: HttpClient) {}

  search() {
    if (!this.query) return;
    this.loading = true;
    this.http.get<any>(`http://localhost:8000/search?q=${encodeURIComponent(this.query)}&k=5`)
      .subscribe(r => { this.results = r.results; this.loading = false; }, () => this.loading = false);
  }

  submitFailure() {
    this.http.post('http://localhost:8000/submit_failure', { error_log: this.query })
      .subscribe();
  }

  feedback(failure_id: number, helpful: boolean) {
    this.http.post('http://localhost:8000/feedback', { failure_id, helpful })
      .subscribe();
  }
}
