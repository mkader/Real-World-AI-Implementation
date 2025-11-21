import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  template: `
    <div class="container">
      <h1>TF Triage Agent</h1>
      <div class="form-group">
        <label for="errorLog">Error Log:</label>
        <textarea 
          id="errorLog" 
          [(ngModel)]="errorLog" 
          rows="8" 
          placeholder="Paste test failure log here...">
        </textarea>
      </div>
      <button (click)="submitFailure()" [disabled]="!errorLog">Submit for Triage</button>
      
      <div *ngIf="result" class="result">
        <h2>Triage Result</h2>
        <pre>{{ result }}</pre>
      </div>
    </div>
  `,
  styles: [`
    .container {
      max-width: 800px;
      margin: 40px auto;
      padding: 20px;
    }
    h1 {
      color: #333;
    }
    .form-group {
      margin: 20px 0;
    }
    label {
      display: block;
      margin-bottom: 8px;
      font-weight: 600;
    }
    textarea {
      width: 100%;
      padding: 12px;
      border: 1px solid #ddd;
      border-radius: 4px;
      font-family: 'Courier New', monospace;
      font-size: 14px;
    }
    button {
      padding: 12px 24px;
      background: #007bff;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 16px;
    }
    button:disabled {
      background: #ccc;
      cursor: not-allowed;
    }
    button:hover:not(:disabled) {
      background: #0056b3;
    }
    .result {
      margin-top: 30px;
      padding: 20px;
      background: #f8f9fa;
      border-radius: 4px;
    }
    pre {
      white-space: pre-wrap;
      word-wrap: break-word;
    }
  `]
})
export class AppComponent {
  errorLog = '';
  result = '';

  async submitFailure() {
    try {
      const response = await fetch('https://symmetrical-space-potato-5xw67rq462p7jg-8000.app.github.dev/submit_failure', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ error_log: this.errorLog, metadata: {} })
      });
      const data = await response.json();
      this.result = `Job queued: ${data.job_id}\n\nCheck worker logs for recommendation.`;
    } catch (error) {
      this.result = `Error: ${error}`;
    }
  }
}
