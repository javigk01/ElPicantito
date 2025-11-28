import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { environment } from '../../../../environments/environment';

@Component({
  selector: 'app-admin-sidebar',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <nav class="col-md-3 col-lg-2 d-md-block bg-light sidebar collapse">
      <div class="position-sticky pt-3">
        <ul class="nav flex-column">
          <li class="nav-item">
            <a class="nav-link" routerLink="/admin/dashboard" 
               routerLinkActive="active" [routerLinkActiveOptions]="{exact: true}">
              <i class="bi bi-speedometer2 me-2"></i>Dashboard
            </a>
          </li>
          <li class="nav-item">
            <a class="nav-link" routerLink="/admin/productos" 
               routerLinkActive="active">
              <i class="bi bi-box me-2"></i>Productos
            </a>
          </li>
          <li class="nav-item">
            <a class="nav-link" routerLink="/admin/adicionales" 
               routerLinkActive="active">
              <i class="bi bi-plus-circle me-2"></i>Adicionales
            </a>
          </li>
          <li class="nav-item">
            <a class="nav-link" routerLink="/admin/usuarios" 
               routerLinkActive="active">
              <i class="bi bi-people me-2"></i>Usuarios
            </a>
          </li>
          <li class="nav-item">
            <button class="nav-link btn-chatbot" (click)="toggleChatbot()">
              <i class="bi bi-robot me-2"></i>Chatbot Admin
            </button>
          </li>
        </ul>
      </div>
    </nav>

    <!-- Modal de Chatbot Admin -->
    <div class="chatbot-modal" *ngIf="showChatbot" (click)="toggleChatbot()">
      <div class="chatbot-container" (click)="$event.stopPropagation()">
        <div class="chatbot-header">
          <h5><i class="bi bi-robot me-2"></i>Chatbot Administrativo</h5>
          <button class="btn-close-chatbot" (click)="toggleChatbot()">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
        <iframe 
          [src]="chatbotUrl" 
          class="chatbot-iframe"
          [attr.frameborder]="0"
        ></iframe>
      </div>
    </div>
  `,
  styles: [`
    .sidebar {
      background-color: var(--neutral-surface);
      border-right: 2px solid var(--neutral-border);
      min-height: calc(100vh - 70px);
    }

    .sidebar .nav-link {
      color: var(--neutral-text);
      padding: 0.75rem 1rem;
      border-radius: 8px;
      margin: 0.25rem 0;
      transition: all 0.3s ease;
    }

    .sidebar .nav-link:hover {
      background-color: var(--primary-light);
      color: var(--primary-hover);
      transform: translateX(5px);
    }

    .sidebar .nav-link.active {
      background-color: var(--primary-color);
      color: white;
    }

    .btn-chatbot {
      width: 100%;
      text-align: left;
      border: none;
      background: transparent;
      cursor: pointer;
    }

    .btn-chatbot:hover {
      background-color: var(--primary-light) !important;
      color: var(--primary-hover) !important;
    }

    /* Modal de Chatbot */
    .chatbot-modal {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background-color: rgba(0, 0, 0, 0.5);
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 9999;
    }

    .chatbot-container {
      width: 80%;
      max-width: 900px;
      height: 80%;
      background-color: white;
      border-radius: 12px;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    .chatbot-header {
      background: linear-gradient(135deg, #ff6b6b, #ff9e00);
      color: white;
      padding: 1rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .chatbot-header h5 {
      margin: 0;
      font-weight: 600;
    }

    .btn-close-chatbot {
      background: rgba(255, 255, 255, 0.2);
      border: none;
      border-radius: 50%;
      width: 32px;
      height: 32px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.3s ease;
    }

    .btn-close-chatbot:hover {
      background: rgba(255, 255, 255, 0.3);
      transform: rotate(90deg);
    }

    .btn-close-chatbot i {
      color: white;
    }

    .chatbot-iframe {
      flex: 1;
      width: 100%;
      border: none;
    }
  `]
})
export class AdminSidebarComponent {
  @Input() activeRoute: string = '';
  showChatbot = false;
  chatbotUrl = environment.chatbotAdminUrl;

  toggleChatbot() {
    this.showChatbot = !this.showChatbot;
  }
}
