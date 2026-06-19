import { useEffect, useState } from "react";
import { Plus, X } from "lucide-react";
import toast from "react-hot-toast";
import { deptApi, posApi } from "@/api/client";
import type { Department, Position, ImplicitTag } from "@/api/types";
import { useAuthStore } from "@/store/auth";

export default function Positions() {
  const [departments, setDepartments] = useState<Department[]>([]);
  const [positions, setPositions] = useState<Position[]>([]);
  const [selPos, setSelPos] = useState<string>("");
  const [newTag, setNewTag] = useState("");
  const user = useAuthStore((s) => s.user);
  const canEdit = user?.role !== "social_lead" && user?.role !== "campus_lead";

  const load = async () => {
    const [ds, ps] = await Promise.all([deptApi.list(), posApi.list()]);
    setDepartments(ds);
    setPositions(ps);
    if (ps.length && !selPos) setSelPos(ps[0].id);
  };

  useEffect(() => { load(); }, []);

  const sel = positions.find((p) => p.id === selPos);

  const addTag = async () => {
    if (!newTag.trim() || !sel) return;
    try {
      const updated = await posApi.addTag(sel.id, { t: newTag.trim(), w: 15 });
      setPositions((ps) => ps.map((p) => (p.id === updated.id ? updated : p)));
      setNewTag("");
      toast.success(`已添加标签「${newTag.trim()}」`);
    } catch {}
  };

  const removeTag = async (name: string) => {
    if (!sel) return;
    try {
      const updated = await posApi.removeTag(sel.id, name);
      setPositions((ps) => ps.map((p) => (p.id === updated.id ? updated : p)));
      toast.success("已移除标签");
    } catch {}
  };

  const toggle = async () => {
    if (!sel) return;
    await posApi.toggle(sel.id);
    await load();
  };

  // 按部门分组
  const grouped = positions.reduce<Record<string, Position[]>>((acc, p) => {
    const k = p.department_name || "其他";
    (acc[k] = acc[k] || []).push(p);
    return acc;
  }, {});

  return (
    <>
      <div className="mb-6">
        <h1 className="text-[23px] font-semibold tracking-tight flex items-center gap-3">
          部门与岗位配置
          <span className="tag tag-blue">关系表全员可见</span>
        </h1>
        <p className="text-text-2 mt-2 text-[13.5px] max-w-[760px]">
          维护「部门 — HRBP(1) — 主管(1) — 锻炼干部(多) — 岗位(多)」关系；JD 与隐性标签是解析/分流的依据。
        </p>
      </div>

      {/* 部门关系对应表 */}
      <div className="flex items-center gap-2 text-[13.5px] font-semibold mb-3.5">
        <div className="w-1.5 h-1.5 rounded-sm bg-blue" />
        部门关系对应表
        <div className="flex-1" />
        {canEdit && <button className="btn btn-primary btn-sm"><Plus size={14} /> 新增关系</button>}
      </div>

      <div className="card card-pad mb-6">
        <table>
          <thead>
            <tr>
              <th>部门</th>
              <th>HRBP（1）</th>
              <th>主管（1）</th>
              <th>锻炼干部（多）</th>
              <th>岗位（多）</th>
            </tr>
          </thead>
          <tbody>
            {departments.map((d) => (
              <tr key={d.id}>
                <td><b>{d.name}</b></td>
                <td>{d.hrbp_id}</td>
                <td>{d.mgr}</td>
                <td>{d.cadres.join("、")}</td>
                <td>
                  <div className="flex flex-wrap gap-1.5">
                    {positions.filter((p) => p.department_id === d.id).map((p) => (
                      <span
                        key={p.id}
                        className="text-[10.5px] font-semibold px-2 py-0.5 rounded"
                        style={{
                          background: p.chan === "社招" ? "#EAF0FF" : "#E1F6F4",
                          color: p.chan === "社招" ? "#1B3FCC" : "#0CA5A0",
                        }}
                      >
                        {p.name}{p.status === "off" && "（下架）"}
                      </span>
                    ))}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* 岗位 JD + 隐性标签 */}
      <div className="flex items-center gap-2 text-[13.5px] font-semibold mb-3.5">
        <div className="w-1.5 h-1.5 rounded-sm bg-blue" />
        岗位 JD 与隐性标签
      </div>

      <div className="grid gap-5" style={{ gridTemplateColumns: "272px 1fr" }}>
        <div className="flex flex-col gap-2.5">
          {Object.entries(grouped).map(([dept, ps]) => (
            <div key={dept}>
              <div className="text-[11px] font-semibold text-text-3 uppercase tracking-wider px-1 pt-1.5 pb-0.5">
                {dept}
              </div>
              {ps.map((p) => (
                <button
                  key={p.id}
                  onClick={() => setSelPos(p.id)}
                  className={`text-left bg-white border rounded-[12px] p-3 transition w-full mb-1.5 ${
                    selPos === p.id ? "border-blue shadow-[0_0_0_3px_#EAF0FF]" : "border-line hover:border-blue"
                  } ${p.status === "off" ? "opacity-60" : ""}`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <b className="text-[13.5px] font-semibold">{p.name}</b>
                    {p.status === "off" ? (
                      <span className="text-[9.5px] font-bold text-red bg-red-soft px-1.5 py-0.5 rounded">已下架</span>
                    ) : (
                      <span
                        className="text-[10.5px] font-semibold px-2 py-0.5 rounded"
                        style={{
                          background: p.chan === "社招" ? "#EAF0FF" : "#E1F6F4",
                          color: p.chan === "社招" ? "#1B3FCC" : "#0CA5A0",
                        }}
                      >
                        {p.chan}
                      </span>
                    )}
                  </div>
                  <div className="text-text-3 text-[11.5px] mt-1">
                    {p.level} · 隐性标签 {p.implicit.length} 项
                  </div>
                </button>
              ))}
            </div>
          ))}
        </div>

        <div className="card card-pad">
          {sel && (
            <>
              <div className="flex items-start justify-between gap-3.5 pb-4 border-b border-line">
                <div>
                  <h3 className="text-[18px] font-semibold">{sel.name}</h3>
                  <div className="text-text-2 text-[12.5px] mt-1.5 flex items-center gap-2 flex-wrap">
                    {sel.department_name} · 职级 {sel.level}
                    <span
                      className="text-[10.5px] font-semibold px-2 py-0.5 rounded"
                      style={{
                        background: sel.chan === "社招" ? "#EAF0FF" : "#E1F6F4",
                        color: sel.chan === "社招" ? "#1B3FCC" : "#0CA5A0",
                      }}
                    >
                      {sel.chan}
                    </span>
                    {sel.status === "off" ? (
                      <span className="text-[10px] font-bold text-red bg-red-soft px-1.5 py-0.5 rounded">已下架</span>
                    ) : (
                      <span className="text-[10px] font-bold text-green bg-green-soft px-1.5 py-0.5 rounded">在架</span>
                    )}
                  </div>
                </div>
                {canEdit && (
                  <div className="flex gap-2">
                    <button className="btn btn-ghost btn-sm" onClick={toggle}>
                      {sel.status === "on" ? "下架" : "上架"}
                    </button>
                  </div>
                )}
              </div>

              <Section title="岗位职责">
                <ul className="list-none grid gap-1.5">
                  {sel.duties.map((d, i) => (
                    <li key={i} className="relative pl-4 text-[13.5px] leading-relaxed before:content-[''] before:absolute before:left-0.5 before:top-2 before:w-1.5 before:h-1.5 before:rounded-full before:bg-blue">
                      {d}
                    </li>
                  ))}
                </ul>
              </Section>

              <Section title="硬性要求">
                <ul className="list-none grid gap-1.5">
                  {sel.must.map((d, i) => (
                    <li key={i} className="relative pl-4 text-[13.5px] leading-relaxed before:content-[''] before:absolute before:left-0.5 before:top-2 before:w-1.5 before:h-1.5 before:rounded-full before:bg-blue">
                      {d}
                    </li>
                  ))}
                </ul>
              </Section>

              <Section title="匹配关键词" note="解析时命中比对">
                <div className="flex gap-1.5 flex-wrap">
                  {sel.keywords.map((k) => (
                    <span key={k} className="text-[10.5px] font-medium px-1.5 py-0.5 rounded bg-blue-soft text-blue-dark">
                      {k}
                    </span>
                  ))}
                </div>
              </Section>

              <Section title="隐性要求标签与权重" note="HRBP 可增减 · 驱动隐性匹配" amber>
                <div className="grid gap-2.5">
                  {(() => {
                    const maxW = Math.max(...sel.implicit.map((t) => t.w), 1);
                    return sel.implicit.map((t) => (
                      <div key={t.t} className="grid items-center gap-3" style={{ gridTemplateColumns: "1fr 130px 38px 26px" }}>
                        <div className="text-[12.5px] text-text">{t.t}</div>
                        <div className="h-2 rounded-full bg-[#F6F8FC] border border-line overflow-hidden">
                          <div
                            className="h-full rounded-full"
                            style={{ width: `${Math.round(t.w / maxW * 100)}%`, background: "linear-gradient(90deg,#C77A0B,#E8A33D)" }}
                          />
                        </div>
                        <div className="font-mono text-[12.5px] font-semibold text-amber text-right">{t.w}%</div>
                        {canEdit ? (
                          <button
                            onClick={() => removeTag(t.t)}
                            className="w-5 h-5 rounded-md flex items-center justify-center text-text-3 bg-[#F6F8FC] border border-line hover:text-red hover:bg-red-soft hover:border-red-soft"
                          >
                            <X size={12} strokeWidth={2.2} />
                          </button>
                        ) : <span />}
                      </div>
                    ));
                  })()}
                </div>
                {canEdit && (
                  <div className="flex gap-2 mt-3">
                    <input
                      className="flex-1 input"
                      value={newTag}
                      onChange={(e) => setNewTag(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && addTag()}
                      placeholder="新增隐性标签，如：交付韧性"
                    />
                    <button className="btn btn-ghost btn-sm" onClick={addTag}>
                      <Plus size={14} /> 添加标签
                    </button>
                  </div>
                )}
              </Section>

              <div className="grid grid-cols-2 gap-3 mt-5 pt-4 border-t border-line">
                <div className="bg-[#F6F8FC] border border-line rounded-[11px] p-3.5">
                  <div className="text-[11.5px] text-text-3">招聘三角色</div>
                  <div className="text-[13.5px] font-semibold mt-1.5 flex flex-col gap-1.5 font-normal text-[12.5px]">
                    {departments.find((d) => d.id === sel.department_id)?.hrbp_id} · HRBP
                    <span>{sel.department_name && departments.find((d) => d.id === sel.department_id)?.mgr} · 主管</span>
                    <span>{departments.find((d) => d.id === sel.department_id)?.cadres.join("、")} · 锻炼干部</span>
                  </div>
                </div>
                <div className="bg-[#F6F8FC] border border-line rounded-[11px] p-3.5">
                  <div className="text-[11.5px] text-text-3">状态</div>
                  <div className="text-[13.5px] font-semibold mt-1.5">
                    {sel.status === "on" ? "在架（参与解析与分流）" : "已下架（不参与匹配）"}
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </>
  );
}

function Section({ title, children, note, amber }: { title: string; children: React.ReactNode; note?: string; amber?: boolean }) {
  return (
    <div className="mt-5">
      <div className="flex items-center gap-2 text-[13px] font-semibold mb-2.5">
        <div className="w-1.5 h-1.5 rounded-sm" style={{ background: amber ? "#C77A0B" : "#2B59FF" }} />
        {title}
        {note && <span className="font-normal text-[11px] text-text-3 bg-[#F6F8FC] px-2 py-0.5 rounded">{note}</span>}
      </div>
      {children}
    </div>
  );
}