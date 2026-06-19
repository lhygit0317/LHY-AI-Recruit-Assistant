// ============ API Client ============
import axios, { AxiosError } from "axios";
import toast from "react-hot-toast";
import { useAuthStore } from "@/store/auth";
import type {
  AnalysisResult, Department, PaginatedResponse, Position, QuestionSet,
  Resume, Token, User,
} from "./types";

export const api = axios.create({
  baseURL: "/api/v1",
  timeout: 60000,
});

// 请求拦截器：自动加 token
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// 响应拦截器：统一错误处理
api.interceptors.response.use(
  (resp) => resp,
  (err: AxiosError<{ detail: string }>) => {
    if (err.response?.status === 401) {
      useAuthStore.getState().logout();
      window.location.href = "/login";
    } else {
      const detail = err.response?.data?.detail || err.message || "请求失败";
      toast.error(detail);
    }
    return Promise.reject(err);
  }
);

// ============ 各模块 API ============
export const authApi = {
  login: (user_id: string, password: string) =>
    api.post<Token>("/auth/login-json", { user_id, password }).then((r) => r.data),
  me: () => api.get<User>("/auth/me").then((r) => r.data),
};

export const userApi = {
  list: (q?: string) =>
    api.get<PaginatedResponse<User>>("/users", { params: { q } }).then((r) => r.data),
  create: (data: any) => api.post<User>("/users", data).then((r) => r.data),
};

export const deptApi = {
  list: () => api.get<Department[]>("/departments").then((r) => r.data),
  create: (data: any) => api.post<Department>("/departments", data).then((r) => r.data),
};

export const posApi = {
  list: (params?: { chan?: string; active_only?: boolean }) =>
    api.get<Position[]>("/positions", { params }).then((r) => r.data),
  get: (id: string) => api.get<Position>(`/positions/${id}`).then((r) => r.data),
  addTag: (id: string, tag: { t: string; w: number }) =>
    api.post<Position>(`/positions/${id}/tags`, tag).then((r) => r.data),
  removeTag: (id: string, tagName: string) =>
    api.delete<Position>(`/positions/${id}/tags/${encodeURIComponent(tagName)}`).then((r) => r.data),
  toggle: (id: string) =>
    api.post<{ message: string }>(`/positions/${id}/toggle`).then((r) => r.data),
};

export const resumeApi = {
  list: (params?: { chan?: string; q?: string }) =>
    api.get<PaginatedResponse<Resume>>("/resumes", { params }).then((r) => r.data),
  get: (id: string) => api.get<Resume>(`/resumes/${id}`).then((r) => r.data),
  recommend: (resumeId: string, deptId: string) =>
    api.post<{ message: string }>(`/resumes/recommend/${resumeId}/to/${deptId}`).then((r) => r.data),
  upload: (file: File, chan: string, deptId: string) => {
    const form = new FormData();
    form.append("file", file);
    return api.post<{ message: string; detail?: string }>("/resumes/upload", form, {
      params: { chan, current_dept_id: deptId },
    }).then((r) => r.data);
  },
};

export const analysisApi = {
  match: (resumeId: string, posId: string) =>
    api.post<AnalysisResult>(`/analysis/match/${resumeId}/${posId}`).then((r) => r.data),
  questions: (resumeId: string, posId: string, useLLM = false) =>
    api.post<QuestionSet>(`/analysis/questions/${resumeId}/${posId}`, null, {
      params: { use_llm: useLLM },
    }).then((r) => r.data),
  route: (resumeId: string) =>
    api.post<any[]>(`/analysis/route/${resumeId}`).then((r) => r.data),
};