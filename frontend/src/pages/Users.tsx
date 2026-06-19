import { useEffect, useState } from "react";
import { Search, Lock, RefreshCw, Plus } from "lucide-react";
import { userApi } from "@/api/client";
import type { User } from "@/api/types";
import { roleColor, roleLabel } from "@/lib/utils";
import { useAuthStore } from "@/store/auth";

export default function Users() {
  const [items, setItems] = useState<User[]>([]);
  const [total, setTotal] = useState(0);
  const [q, setQ] = useState("");
  const user = useAuthStore((s) => s.user);
  const isAdmin = user?.role === "admin";

  useEffect(() => {
    userApi.list(q || undefined).then((d) => {
      setItems(d.items);
      setTotal(d.total);
    });
  }, [q]);

  if (!isAdmin) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-text-3">
        <Lock size={48} className="mb-4 opacity-50" />
        <b className="text-text-2 font-semibold text-[15px]">无权访问</b>
        <span className="mt-2 text-[12.5px]">用户管理仅管理员可访问，当前角色为「{user && roleLabel(user.role)}」</span>
      </div>
    );
  }

  return (
    <>
      <div className="mb-6">
        <h1 className="text-[23px] font-semibold tracking-tight flex items-center gap-3">
          用户管理
          <span className="tag tag-violet">角色后台管理</span>
        </h1>
        <p className="text-text-2 mt-2 text-[13.5px] max-w-[760px]">
          维护参与招聘的用户及其角色。角色在此后台分配。仅管理员可新增 / 编辑 / 停用。
        </p>
      </div>

      <div className="flex justify-between items-center mb-4 flex-wrap gap-3">
        <div className="flex items-center gap-2.5 bg-white border border-line rounded-[10px] py-2 px-3.5 w-[300px]">
          <Search size={15} strokeWidth={2} className="text-text-3" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="搜索姓名 / 工号 / 部门…"
            className="border-none outline-none text-[13px] bg-transparent flex-1"
          />
        </div>
        <div className="flex gap-2.5">
          <button className="btn btn-ghost btn-sm"><RefreshCw size={14} /> 从 W3 同步</button>
          <button className="btn btn-primary btn-sm"><Plus size={14} /> 新增用户</button>
        </div>
      </div>

      <div className="card card-pad">
        <table>
          <thead>
            <tr>
              <th>姓名</th>
              <th>工号</th>
              <th>邮箱</th>
              <th>角色</th>
              <th>部门</th>
              <th>状态</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {items.map((u) => (
              <tr key={u.id}>
                <td>
                  <div className="flex items-center gap-2">
                    <div className="w-[25px] h-[25px] rounded-md bg-[#F6F8FC] border border-line flex items-center justify-center text-[10.5px] font-semibold text-text-2">
                      {u.name[0]}
                    </div>
                    <b className="text-[13px]">{u.name}</b>
                  </div>
                </td>
                <td className="font-mono text-[12px]">{u.id}</td>
                <td className="font-mono text-[12px] text-text-2">{u.email}</td>
                <td>
                  <span className={`pill ${roleColor(u.role)}`}>{roleLabel(u.role)}</span>
                </td>
                <td>{u.dept}</td>
                <td>
                  <span className="text-green font-semibold">{u.status}</span>
                </td>
                <td className="text-right">
                  <span className="text-blue font-semibold text-[12.5px] cursor-pointer">编辑</span>
                  <span className="ml-2 text-red font-semibold text-[12.5px] cursor-pointer">停用</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="text-text-3 text-[12.5px] mt-3 text-right">共 {total} 人</div>
      </div>
    </>
  );
}