export type User = {
  id: string
  email: string
  full_name: string | null
  is_active: boolean
  created_at: string
}

export type OrganizationMembership = {
  id: string
  organization_id: string
  user_id: string
  role: string
  is_pending: boolean
}

export type AuthMe = {
  user: User
  memberships: OrganizationMembership[]
}

export type Organization = {
  id: string
  name: string
  slug: string
  plan: string
  subscription_status: string
  location_limit: number
  keyword_limit: number
}

export type TokenResponse = {
  access_token: string
  refresh_token: string
  token_type: string
}

export type GoogleAccount = {
  id: string
  google_email: string
  created_at: string
}

export type GoogleBusinessProfile = {
  id: string
  organization_id: string
  google_account_id: string
  google_location_name: string
  primary_category: string | null
  website_url: string | null
  phone_number: string | null
  address_formatted: string | null
  address_city: string | null
  is_verified: boolean
  is_suspended: boolean
  is_disconnected: boolean
  review_count: number | null
  average_rating: number | null
  completeness_score: number | null
  last_synced_at: string | null
}

export type AuditRecommendation = {
  category: string
  priority: string
  title: string
  description: string
  action_items: string[]
}

export type AuditReport = {
  id: string
  google_profile_id: string
  status: string
  visibility_score: number | null
  completeness_score: number | null
  review_score: number | null
  engagement_score: number | null
  recommendations: AuditRecommendation[] | null
  completed_at: string | null
  created_at: string
}

export type Review = {
  id: string
  google_profile_id: string
  google_review_id: string
  author_name: string | null
  rating: number | null
  comment: string | null
  review_time: string | null
  reply_text: string | null
  replied_at: string | null
  sentiment: string | null
  is_flagged: boolean
}

export type ReviewListResponse = {
  reviews: Review[]
  total: number
}

export type Post = {
  id: string
  google_profile_id: string
  google_post_id: string | null
  post_type: string
  summary: string
  state: string
  scheduled_at: string | null
  published_at: string | null
  call_to_action_type: string | null
  call_to_action_url: string | null
  created_at: string
}

export type PostListResponse = {
  posts: Post[]
  total: number
}

export type AutomationRule = {
  id: string
  organization_id: string
  rule_type: string
  name: string
  description: string | null
  is_active: boolean
  config: Record<string, unknown> | null
  created_at: string
}

export type Project = {
  id: string
  owner_id: string
  name: string
  slug: string
  description: string | null
  created_at: string
}

export type TargetLocation = {
  id: string
  project_id: string
  label: string
  latitude: number | null
  longitude: number | null
  city: string | null
  country_code: string | null
  created_at: string
}

export type Keyword = {
  id: string
  project_id: string
  target_location_id: string
  phrase: string
  tracking_frequency_minutes: number
  is_active: boolean
  created_at: string
}

export type AgencyBranding = {
  id: string
  organization_id: string
  agency_name: string | null
  logo_url: string | null
  brand_color: string | null
  custom_domain: string | null
  reply_from_email: string | null
  report_footer_text: string | null
  hide_platform_branding: boolean
  created_at: string
  updated_at: string
}

export type ClientLink = {
  id: string
  agency_org_id: string
  client_org_id: string
  client_org_name: string
  client_org_plan: string
  is_active: boolean
  linked_at: string
}

export type AgencyClientSummary = {
  client_org_id: string
  client_org_name: string
  plan: string
  location_count: number
  avg_visibility_score: number | null
  open_review_count: number
  last_audit_at: string | null
}

export type AgencyDashboard = {
  total_clients: number
  total_locations: number
  avg_visibility_score: number | null
  clients: AgencyClientSummary[]
}
