import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authApi } from "@/api/client";
import { useAuthStore } from "@/store/auth";
import toast from "react-hot-toast";

export default function Login() {
  const [userId, setUserId] = useState("H2087");
  const [password, setPassword] = useState("123456");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.setAuth);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await authApi.login(userId, password);
      setAuth(data.access_token, data.user);
      toast.success(`欢迎，${data.user.name}`);
      navigate("/");
    } catch {
      // 错误已由 interceptor toast
    } finally {
      setLoading(false);
    }
  };

  const quickLogin = (id: string) => {
    setUserId(id);
    setPassword("123456");
  };

  return (
    <div className="min-h-screen flex bg-ink">
      {/* 左侧装饰 */}
      <div
        className="hidden lg:flex flex-1 flex-col justify-between p-12 text-white"
        style={{
          background:
            "radial-gradient(120% 120% at 0% 0%, #1E3F94 0%, #0F121A 56%)",
          position: "relative",
          overflow: "hidden",
        }}
      >
        <div className="flex items-center gap-3 relative z-10">
          <div
            className="w-9 h-9 rounded-[10px] relative"
            style={{
              background: "linear-gradient(135deg, #3B6BFF, #0CA5A0)",
            }}
          />
          <b className="text-base font-semibold">算力事业部 · 招聘智能助手</b>
        </div>

        <h2 className="text-[35px] font-semibold leading-tight tracking-tight max-w-[460px] relative z-10">
          让每一份简历，<br />
          都落到<em className="not-italic" style={{ background: "linear-gradient(90deg,#6E98FF,#42DACF)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>对的部门和人</em>手里。
        </h2>

        <div className="text-xs text-[#8893A6] leading-relaxed relative z-10">
          通过 W3 统一身份认证登录 · 角色由后台管理下发<br />
          数据权限随角色生效 · 操作全程留痕
        </div>
      </div>

      {/* 右侧登录 */}
      <div className="w-full lg:w-[470px] bg-white flex flex-col justify-center px-12 py-14 overflow-y-auto">
        <h3 className="text-[22px] font-semibold">登录</h3>
        <p className="text-text-2 text-[13.5px] mt-2 mb-6">企业内部系统，通过工号 + 密码登录。</p>

        <form onSubmit={submit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-text-2 mb-2">工号</label>
            <input
              className="input"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              placeholder="如 H2087"
              autoFocus
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-text-2 mb-2">密码</label>
            <input
              type="password"
              className="input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary w-full mt-2"
          >
            {loading ? "登录中…" : "登录"}
          </button>
        </form>

        <div className="flex items-center gap-3 my-6 text-text-3 text-[11.5px]">
          <div className="flex-1 h-px bg-line" />
          演示账号（密码统一：123456）
          <div className="flex-1 h-px bg-line" />
        </div>

        <div className="grid grid-cols-2 gap-2">
          {[
            { id: "A0001", name: "管理员", role: "admin" },
            { id: "D1001", name: "周明 (HRD)", role: "hrd" },
            { id: "H2087", name: "张敏 (HRBP)", role: "hrbp" },
            { id: "S2001", name: "孙磊 (社招)", role: "social_lead" },
            { id: "X3001", name: "陈晨 (校招)", role: "campus_lead" },
            { id: "H3056", name: "郑燕 (HRBP)", role: "hrbp" },
          ].map((u) => (
            <button
              key={u.id}
              type="button"
              onClick={() => quickLogin(u.id)}
              className="flex items-center gap-2 p-2.5 border border-line rounded-lg text-left hover:border-blue hover:shadow-sh transition"
            >
              <div className="w-9 h-9 rounded-md bg-ink text-white flex items-center justify-center font-semibold text-sm">
                {u.name[0]}
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-[13px] font-semibold truncate">{u.name}</div>
                <div className="text-[10px] text-text-3 font-mono">工号 {u.id}</div>
              </div>
            </button>
          ))}
        </div>

        <div className="mt-5 text-[11.5px] text-text-3 leading-relaxed p-3 bg-[#F6F8FC] border border-line rounded-md">
          不同角色权限不同：<b>管理员</b>维护用户；<b>HRD</b>看全部；<b>HRBP</b>看本人名下；<b>社招/校招负责人</b>按渠道查看。
        </div>
      </div>
    </div>
  );
}