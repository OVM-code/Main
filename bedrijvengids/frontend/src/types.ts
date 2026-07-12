export interface Company {
  id: number
  search_id: number
  name: string
  address: string | null
  gemeente: string | null
  phone: string | null
  email: string | null
  website: string | null
  category: string | null
  lat: number | null
  lon: number | null
  facebook: string | null
  instagram: string | null
  linkedin: string | null
  description: string | null
  vat: string | null
  zaakvoerder: string | null
  contacted: boolean
  contacted_at: string | null
  enriched: boolean
  ai_email_subject: string | null
  ai_email_body: string | null
  ai_linkedin_message: string | null
}

export interface Search {
  id: number
  sector: string
  location: string
  country: string
  kind: string
  functie: string | null
  credits_used: number
  created_at: string
  company_count: number
}

export interface SearchDetail extends Search {
  companies: Company[]
}

export interface Employee {
  id: number
  company_id: number
  name: string
  role: string | null
  level: string | null
  email: string | null
  phone: string | null
  linkedin: string | null
  source: string | null
}

export interface Person {
  id: number
  name: string
  role: string | null
  level: string | null
  email: string | null
  phone: string | null
  linkedin: string | null
  company_id: number
  company_name: string
  gemeente: string | null
  sector: string | null
  website: string | null
}

export interface Template {
  kind: string
  subject: string | null
  body: string
  personalization: 'basic' | 'ai'
}

export interface Stats {
  search_count: number
  company_count: number
  monthly_credits_used: number
  monthly_credit_limit: number
}

export interface Message {
  subject: string | null
  body: string
  to: string | null
  mailto: string | null
  source: 'basic' | 'ai'
}
