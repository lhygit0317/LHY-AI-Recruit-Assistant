// ============ 类型定义 ============
export type Role = "admin" | "hrd" | "hrbp" | "social_lead" | "campus_lead";

export interface User {
  id: string;
  name: string;
  email: string;
  role: Role;
  dept: string;
  status: string;
  is_active: boolean;
  created_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Department {
  id: string;
  name: string;
  hrbp_id: string;
  mgr: string;
  cadres: string[];
  created_at: string;
  position_count: number;
}

export interface ImplicitTag { t: string; w: number; }

export interface Position {
  id: string;
  name: string;
  chan: string;
  level: string;
  department_id: string;
  department_name: string;
  duties: string[];
  must: string[];
  keywords: string[];
  implicit: ImplicitTag[];
  status: "on" | "off";
  created_at: string;
}

export interface Resume {
  id: string;
  name: string;
  chan: "社招" | "校招";
  pos: string;
  owner_id: string;
  owner_name: string;
  current_dept_id: string;
  current_dept_name: string;
  source: "导入" | "推荐" | "批量导入";
  by_user_id: string | null;
  by_user_name: string | null;
  file_path: string | null;
  raw_text: string | null;
  keywords: string[];
  traits: string[];
  exp_base: number;
  education: any[];
  experience: any[];
  created_at: string;
  updated_at: string;
}

export interface AnalysisResult {
  skill: number;
  exp: number;
  implicit: number;
  total: number;
  k_hit: string[];
  k_miss: string[];
  t_hit: string[];
  t_miss: string[];
  verdict: string;
  summary: string;
}

export interface QuestionItem { q: string; why: string; lvl: string; }
export interface QuestionSet {
  专业: QuestionItem[];
  主管: QuestionItem[];
  资格: QuestionItem[];
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}