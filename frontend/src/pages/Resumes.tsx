import { useEffect, useState } from "react";
import { Search, Trash2, Upload, Bell } from "lucide-react";
import toast from "react-hot-toast";
import { resumeApi } from "@/api/client";
import type { Resume } from "@/api/types";

export default function Resumes() {
  const [items, setItems] = useState<Resume[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [chan, setChan] = useState<"社招" | "校招" | "">("");
  const [q, setQ] = useState("");

  const load = async () => {
    setLoading(true);
    try {
      const data = await resumeApi.list({
        chan: chan || undefined,
        q: q || undefined,
      });
      setItems(data.items);
      setTotal(data.total);
    } catch {}
    setLoading(false);
  };

  useEffect(() => { load(); }, [chan, q]);

  return (
    <>
      <div className="mb-6">
        <h1 className="text-[23px] font-semibold tracking-tight flex items-center gap-3">
          简历库
          <span className="tag tag-blue">PostgreSQL · 区分社招/校招</span>
        </h1>
        <p className="text-text-2 mt-2 text-[13.5px] max-w-[760px]">
          集中存储简历，区分社招与校招，记录当前部门归属与来源；支持关键词检索、批量导入与手动删除。
        </p>
      </div>

      {/* 推荐提醒 banner */}
      <div className="flex items-center gap-3 bg-gradient-to-r from-teal-soft to-white border border-[#BCE7E2] rounded-[13px] p-3.5 mb-5">
        <div className="w-[38px] h-[38px] rounded-[11px] bg-white border border-[#BCE7E2] flex items-center justify-center flex-shrink-0">
          <Bell size={19} strokeWidth={1.8} className="text-teal" />
        </div>
        <div className="flex-1 text-[13px]">
          <b className="font-semibold">有 2 份简历被推荐到你名下</b>
          <br />
          <span className="text-text-2 text-[12px]">周晓（锻炼干部 王浩）、林一帆（校招负责人 陈晨）</span>
        </div>
        <button className="btn btn-ghost btn-sm">标记已读</button>
      </div>

      <div className="tabs mb-4">
        <button className={chan === "" ? "on" : ""} onClick={() => setChan("")}>
          全部 <span className="ml-1.5 text-[10.5px] opacity-55 font-mono">{total}</span>
        </button>
        <button className={chan === "社招" ? "on" : ""} onClick={() => setChan("社招")}>
          社招
        </button>
        <button className={chan === "校招" ? "on" : ""} onClick={() => setChan("校招")}>
          校招
        </button>
      </div>

      <div className="flex justify-between items-center mb-4 gap-3 flex-wrap">
        <div className="flex items-center gap-2.5 bg-white border border-line rounded-[10px] py-2 px-3.5 w-[300px]">
          <Search size={15} strokeWidth={2} className="text-text-3" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="搜索姓名 / 岗位 / 关键词…"
            className="border-none outline-none text-[13px] bg-transparent flex-1"
          />
        </div>
        <div className="flex gap-2">
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => toast("批量导入待 Day 3 完善")}
          >
            <Upload size={15} /> 批量导入
          </button>
        </div>
      </div>

      <div className="card card-pad">
        {loading ? (
          <div className="text-center text-text-3 py-12">加载中…</div>
        ) : items.length === 0 ? (
          <div className="text-center text-text-3 py-12">该渠道下暂无简历</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>候选人</th>
                <th>当前部门</th>
                <th>意向岗位</th>
                <th>来源</th>
                <th>关键词</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {items.map((r) => (
                <tr key={r.id}>
                  <td>
                    <div className="flex items-center gap-2">
                      <div className="w-[25px] h-[25px] rounded-md bg-[#F6F8FC] border border-line flex items-center justify-center text-[10.5px] font-semibold text-text-2">
                        {r.name[0]}
                      </div>
                      <b className="text-[13px]">{r.name}</b>
                    </div>
                    <div className="text-[11px] text-text-3 mt-0.5">
                      归属 {r.owner_name || r.owner_id}
                    </div>
                  </td>
                  <td><b>{r.current_dept_name}</b></td>
                  <td>{r.pos}</td>
                  <td>
                    {r.source === "推荐" ? (
                      <span className="src-tag src-ref" style={{ background: "#E1F6F4", color: "#0CA5A0", fontSize: "10.5px", fontWeight: 600, padding: "2px 8px", borderRadius: "5px" }}>
                        推荐
                      </span>
                    ) : (
                      <span style={{ background: "#EEF1F6", color: "#475069", fontSize: "10.5px", fontWeight: 600, padding: "2px 8px", borderRadius: "5px" }}>
                        本人导入
                      </span>
                    )}
                  </td>
                  <td>
                    <div className="flex gap-1 flex-wrap">
                      {r.keywords.map((k) => (
                        <span key={k} className="text-[10.5px] font-medium px-1.5 py-0.5 rounded bg-blue-soft text-blue-dark">
                          {k}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="text-right">
                    <button
                      className="text-red font-semibold text-[12.5px]"
                      onClick={() => toast("Day 3 完善删除")}
                    >
                      <Trash2 size={14} className="inline" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}