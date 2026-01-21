// API Response Types - matches backend schemas

export interface Member {
  id: number;
  name: string;
  email: string | null;
  phone: string | null;
  created_at: string;
}

export interface EntryResponse {
  id: number;
  member_id: number;
  member_name: string;
  timestamp: string;
  notes: string | null;
  message: string;
}

export interface PaymentResponse {
  id: number;
  member_id: number;
  member_name: string;
  amount: number;
  timestamp: string;
  notes: string | null;
  message: string;
}

export interface MemberSummary {
  member: Member;
  stats: {
    total_entries: number;
    total_payments: number;
    total_amount_paid: number;
    last_entry: string | null;
    last_payment: string | null;
  };
}

export interface ApiError {
  detail: string;
  error_code?: string;
}

// Request types
export interface EntryRequest {
  member_id: number;
  notes?: string;
}

export interface PaymentRequest {
  member_id: number;
  amount: number;
  notes?: string;
}
