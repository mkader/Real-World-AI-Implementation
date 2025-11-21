import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { TriageSearchComponent } from './triage-search/triage-search.component';

@NgModule({
  declarations: [TriageSearchComponent],
  imports: [BrowserModule, FormsModule, HttpClientModule],
  providers: [],
  bootstrap: [TriageSearchComponent]
})
export class AppModule { }
