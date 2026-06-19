import { useEffect, useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import {
  ScanLine, GitBranch, Database, Settings, Users as UsersIcon, LogOut, Bell,
} from "lucide-react";
import { useAuthStore } from "@/store/auth";
import { roleColor, roleLabel } from "@/lib/utils";
import toast from "react-hot-toast";

const navItems = [
  { group: "智能处理" },
  { to: "/parse", label: "简历解析", icon: ScanLine },
  { to: "/recommend", label: "简历推荐", icon: GitBranch },
  { group: "简历数据" },
  { to: "/resumes", label: "简历库", icon: Database },
  { group: "基础配置" },
  { to: "/positions", label: "部门与岗位配置", icon: Settings },
  { to: "/users", label: "用户管理", icon: UsersIcon, adminOnly: true },
];

const titles: Record<string, string> = {
  "/parse": "简历解析",
  "/recommend": "简历推荐",
  "/resumes": "简历库",
  "/positions": "部门与岗位配置",
  "/users": "用户管理",
};

export default function Layout() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const navigate = useNavigate();
  const location = useLocation();
  const [userMenu, setUserMenu] = useState(false);
  const [bellMenu, setBellMenu] = useState(false);
  const [bellCount] = useState(0); // TODO: 接通知 API

  useEffect(() => {
    const onClick = () => { setUserMenu(false); setBellMenu(false); };
    document.addEventListener("click", onClick);
    return () => document.removeEventListener("click", onClick);
  }, []);

  const handleLogout = () => {
    logout();
    toast.success("已退出");
    navigate("/login");
  };

  return (
    <div className="grid grid-cols-[244px_1fr] grid-rows-[60px_1fr] h-screen"
      style={{ gridTemplateAreas: '"side top" "side main"' }}>
      {/* Sidebar */}
      <aside
        className="text-[#C5CDDC] flex flex-col overflow-hidden"
        style={{
          gridArea: "side",
          background: "linear-gradient(180deg,#171B26,#0F121A)",
        }}
      >
        <div className="p-5 pb-4 flex items-center gap-3 border-b border-white/10">
          <div
            className="w-[34px] h-[34px] rounded-[10px] flex-shrink-0"
            style={{
              background: "linear-gradient(135deg,#3B6BFF,#0CA5A0)",
              boxShadow: "inset 0 0 0 1px rgba(255,255,255,.12)",
              position: "relative",
            }}
          />
          <div>
            <b className="text-white text-[14.5px] font-semibold block">招聘智能助手</b>
            <span className="text-[11px] text-[#7A859A] block">算力事业部</span>
          </div>
        </div>

        <nav className="flex-1 overflow-y-auto p-3">
          {navItems.map((item, idx) =>
            item.group ? (
              <div key={idx} className="text-[10.5px] tracking-wider text-[#5E6A7F] uppercase px-2.5 pt-3.5 pb-1.5 font-semibold">
                {item.group}
              </div>
            ) : item.adminOnly && user?.role !== "admin" ? null : (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-2.5 px-2.5 py-2.5 rounded-[10px] text-[13.5px] mb-0.5 transition ${
                    isActive
                      ? "bg-gradient-to-r from-[rgba(43,89,255,.26)] to-[rgba(43,89,255,.05)] text-white"
                      : "text-[#BFC8D8] hover:bg-white/5 hover:text-white"
                  }`
                }
              >
                <item.icon size={18} strokeWidth={1.8} />
                {item.label}
              </NavLink>
            )
          )}
        </nav>

        <div className="p-3.5 border-t border-white/10 text-[11px] text-[#69748A] leading-relaxed">
          v0.1.0 · 2 周 MVP<br />数据权限按角色隔离
        </div>
      </aside>

      {/* Topbar */}
      <header
        className="bg-white/85 backdrop-blur border-b border-line flex items-center justify-between px-7 z-20"
        style={{ gridArea: "top" }}
      >
        <div className="text-[13px] text-text-2">
          <b className="text-text font-semibold text-[15px]">
            {titles[location.pathname] || "招聘智能助手"}
          </b>
        </div>

        <div className="flex items-center gap-4">
          {/* 通知 */}
          <div className="relative">
            <button
              onClick={(e) => { e.stopPropagation(); setBellMenu(!bellMenu); setUserMenu(false); }}
              className="relative w-[38px] h-[38px] rounded-[10px] flex items-center justify-center bg-[#F6F8FC] border border-line hover:bg-[#EAEEF6] transition"
            >
              <Bell size={18} strokeWidth={1.8} className="text-text-2" />
              {bellCount > 0 && (
                <span className="absolute top-1.5 right-2 min-w-[15px] h-[15px] rounded-full bg-red text-white text-[9.5px] font-bold flex items-center justify-center px-0.5 border-2 border-white">
                  {bellCount}
                </span>
              )}
            </button>
          </div>

          {/* 用户菜单 */}
          <div className="relative">
            <button
              onClick={(e) => { e.stopPropagation(); setUserMenu(!userMenu); setBellMenu(false); }}
              className="flex items-center gap-2.5 px-2 pr-1.5 py-1 rounded-full bg-[#F6F8FC] border border-line hover:bg-[#EAEEF6] transition"
            >
              <div className="text-right leading-tight">
                <div className="text-[13px] font-semibold">{user?.name}</div>
                <div className="text-[10px] text-text-3 font-mono">工号 {user?.id}</div>
              </div>
              <div
                className="w-[33px] h-[33px] rounded-full text-white flex items-center justify-center font-semibold text-[13px]"
                style={{ background: "linear-gradient(135deg,#3B6BFF,#0CA5A0)" }}
              >
                {user?.name?.[0] || "?"}
              </div>
            </button>
            {userMenu && (
              <div className="absolute right-0 top-[50px] w-[240px] bg-white border border-line rounded-[13px] shadow-sh-lg p-2 z-40">
                <div className="p-2.5 border-b border-line mb-1.5">
                  <b className="text-[13.5px] block">{user?.name}</b>
                  <span className="text-[11px] text-text-3 font-mono">
                    {user && roleLabel(user.role)} · 工号 {user?.id}
                  </span>
                  <span className={`pill ${user && roleColor(user.role)} mt-1.5 inline-block`}>
                    {user && roleLabel(user.role)}
                  </span>
                </div>
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-2 w-full p-2.5 rounded-md text-[13px] text-left hover:bg-[#F6F8FC]"
                >
                  <LogOut size={15} strokeWidth={1.8} className="text-text-2" />
                  退出登录
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="overflow-y-auto p-8" style={{ gridArea: "main" }}>
        <Outlet />
      </main>
    </div>
  );
}