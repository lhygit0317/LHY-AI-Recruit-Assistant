// ============ 工具函数 ============
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function scoreColor(s: number): string {
  if (s >= 80) return "#1E9E54"; // green
  if (s >= 65) return "#C77A0B"; // amber
  return "#D2453F"; // red
}

export function verdictText(s: number): { text: string; cls: string } {
  if (s >= 80) return { text: "强烈推荐", cls: "tag-green" };
  if (s >= 65) return { text: "建议进入面试", cls: "tag-amber" };
  return { text: "谨慎 / 暂不推荐", cls: "tag-red" };
}

export function roleLabel(role: string): string {
  return {
    admin: "管理员", hrd: "HRD", hrbp: "HRBP",
    social_lead: "社招负责人", campus_lead: "校招负责人",
  }[role] || role;
}

export function roleColor(role: string): string {
  return {
    admin: "tag-violet", hrd: "tag-amber", hrbp: "tag-blue",
    social_lead: "tag-blue", campus_lead: "tag-teal",
  }[role] || "tag-blue";
}