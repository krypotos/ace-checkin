// API Service - handles all backend communication

import { API_CONFIG, apiUrl } from '../config/api';
import type {
  Member,
  EntryResponse,
  PaymentResponse,
  MemberSummary,
  EntryRequest,
  PaymentRequest,
  ApiError,
} from '../types/api';

class ApiService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = apiUrl(endpoint);

    const config: RequestInit = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.timeout);

      const response = await fetch(url, {
        ...config,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const error: ApiError = await response.json().catch(() => ({
          detail: `HTTP ${response.status}: ${response.statusText}`,
        }));
        throw new ApiServiceError(error.detail, response.status);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof ApiServiceError) {
        throw error;
      }
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw new ApiServiceError('Request timed out', 408);
        }
        throw new ApiServiceError(
          `Network error: ${error.message}`,
          0
        );
      }
      throw new ApiServiceError('Unknown error occurred', 0);
    }
  }

  // ==================== Member Operations ====================

  /**
   * Get member by ID
   * Use after scanning barcode to verify member exists and get their name
   */
  async getMember(memberId: number): Promise<Member> {
    return this.request<Member>(`${API_CONFIG.endpoints.members}/${memberId}`);
  }

  /**
   * Get member summary with stats
   * Shows total entries, payments, etc.
   */
  async getMemberSummary(memberId: number): Promise<MemberSummary> {
    return this.request<MemberSummary>(API_CONFIG.endpoints.memberSummary(memberId));
  }

  // ==================== Entry Operations ====================

  /**
   * Log a member entry (court check-in)
   */
  async logEntry(data: EntryRequest): Promise<EntryResponse> {
    return this.request<EntryResponse>(API_CONFIG.endpoints.entry, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // ==================== Payment Operations ====================

  /**
   * Log a member payment
   */
  async logPayment(data: PaymentRequest): Promise<PaymentResponse> {
    return this.request<PaymentResponse>(API_CONFIG.endpoints.payment, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // ==================== Health Check ====================

  /**
   * Check if the API server is reachable
   */
  async healthCheck(): Promise<boolean> {
    try {
      await this.request<{ status: string }>('/health');
      return true;
    } catch {
      return false;
    }
  }
}

// Custom error class for API errors
export class ApiServiceError extends Error {
  constructor(
    message: string,
    public statusCode: number
  ) {
    super(message);
    this.name = 'ApiServiceError';
  }

  get isNotFound(): boolean {
    return this.statusCode === 404;
  }

  get isValidationError(): boolean {
    return this.statusCode === 422;
  }

  get isNetworkError(): boolean {
    return this.statusCode === 0;
  }

  get isTimeout(): boolean {
    return this.statusCode === 408;
  }
}

// Export singleton instance
export const api = new ApiService();
