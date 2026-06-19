import { useEffect, useState } from "react";
import { GitBranch, ArrowRight, Sparkles } from "lucide-react";
import { analysisApi, resumeApi } from "@/api/client";
import type { Resume } from "@/api/types";
import { scoreColor } from "@/lib/utils";
import toast from "react-hot-toast";

interface RouteResult {
  dept_id: string;
  dept_name: string;
  hrbp_id: string;
  mgr: string;
  cadres: string[];
  position_id: string;
  position_name: string;
  score: number;
}

export default function Recommend() {
  const [chan, setChan] = useState<"社招" | "校招">("社招");
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [selResume, setSelResume] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<RouteResult[]>([]);
  const [routed, setRouted] = useState(false);

  useEffect(() => {
    resumeApi.list({ chan }).then((d) => {
      setResumes(d.items);
      if (d.items.length) setSelResume(d.items[0].id);
      setRouted(false);
    });
  }, [chan]);

  const run = async () => {
    if (!selResume) return;
    setLoading(true);
    setRouted(false);
    try {
      const data = await analysisApi.route(selResume);
      setResults(data);
      setRouted(true);
    } catch {} finally {
      setLoading(false);
    }
  };

  const resume = resumes.find((r) => r.id === selResume);
  const best = results[0];

  return (
    <>
      <div className="mb-6">
        <h1 className="text-[23px] font-semibold tracking-tight flex items-center gap-3">
          简历推荐
          <span className="tag tag-teal">智能分流</span>
        </h1>
        <p className="text-text-2 mt-2 text-[13.5px] max-w-[760px]">
          选择库中简历或导入新简历，系统在各部门间智能分流，给出最匹配的部门/岗位并带出 HRBP、主管、锻炼干部，可直接「推荐到」对应名下。
        </p>
      </div>

      <div className="tabs mb-5">
        <button className={chan === "社招" ? "on" : ""} onClick={() => setChan("社招")}>
          社招 <span className="ml-1.5 text-[10.5px] opacity-55 font-mono">SOCIAL</span>
        </button>
        <button className={chan === "校招" ? "on" : ""} onClick={() => setChan("校招")}>
          校招 <span className="ml-1.5 text-[10.5px] opacity-55 font-mono">CAMPUS</span>
        </button>
      </div>

      <div className="grid gap-5" style={{ gridTemplateColumns: "392px 1fr" }}>
        <div className="card card-pad">
          <div className="flex items-center gap-2 text-[13.5px] font-semibold mb-3.5">
            <div className="w-1.5 h-1.5 rounded-sm bg-teal" /> 选择待分流简历
          </div>

          <div className="mt-4">
            <label className="block text-xs font-semibold text-text-2 mb-2">选择简历</label>
            <select className="input" value={selResume} onChange={(e) => { setSelResume(e.target.value); setRouted(false); }}>
              {resumes.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name} · {r.pos} · {r.current_dept_name}
                </option>
              ))}
            </select>
          </div>

          <button className="btn btn-primary w-full mt-4" onClick={run} disabled={!selResume || loading}>
            <GitBranch size={16} /> {loading ? "分流中…" : "智能分流"}
          </button>
        </div>

        <div>
          {!routed ? (
            <div className="card card-pad flex flex-col items-center justify-center min-h-[440px] text-text-3 border-dashed bg-[#F6F8FC]">
              <Sparkles size={42} className="mb-3.5 opacity-50" />
              <b className="text-text-2 font-semibold text-[14px]">分流结果将显示在这里</b>
              <span className="mt-1.5 text-[12.5px]">选择简历后点击「智能分流」</span>
            </div>
          ) : (
            <div className="card card-pad">
              {resume && (
                <div className="flex items-center gap-3.5 pb-4 border-b border-line mb-4">
                  <div className="w-10 h-10 rounded-[11px] bg-ink text-white flex items-center justify-center font-semibold">
                    {resume.name[0]}
                  </div>
                  <div>
                    <h3 className="text-[16px] font-semibold flex items-center gap-2">
                      {resume.name}
                      <span className="text-[10.5px] font-semibold px-2 py-0.5 rounded bg-blue-soft text-blue">
                        {resume.chan}
                      </span>
                    </h3>
                    <div className="text-text-2 text-[12px]">关键词：{resume.keywords.join("、")}</div>
                  </div>
                </div>
              )}

              <div className="grid gap-3">
                {results.map((r, i) => (
                  <div
                    key={r.dept_id}
                    className={`rounded-[13px] p-4 grid items-center gap-4 border ${
                      i === 0 ? "border-green bg-gradient-to-r from-green-soft to-white" : "border-line bg-white"
                    }`}
                    style={{ gridTemplateColumns: "auto 1fr auto" }}
                  >
                    <div className="flex flex-col items-center w-[60px]">
                      <b className="font-mono text-[23px] font-bold leading-none" style={{ color: scoreColor(r.score) }}>
                        {r.score}
                      </b>
                      <small className="text-[10px] text-text-3">匹配</small>
                    </div>

                    <div>
                      <h4 className="text-[15px] font-semibold flex items-center gap-2">
                        {r.dept_name}
                        {i === 0 && (
                          <span className="text-[10.5px] font-bold text-green bg-white border border-green px-2 py-0.5 rounded">
                            最佳去向
                          </span>
                        )}
                      </h4>
                      <div className="text-text-2 text-[12.5px] mt-0.5">推荐岗位：{r.position_name}</div>
                      <div className="flex gap-4 mt-2.5 flex-wrap">
                        <Person avatar={r.hrbp_id[0]} name={r.hrbp_id} role="HRBP" />
                        <Person avatar={r.mgr[0]} name={r.mgr} role="主管" />
                        <Person avatar={r.cadres[0]?.[0] || "?"} name={r.cadres.join("、")} role="锻炼干部" />
                      </div>
                    </div>

                    <button
                      className={i === 0 ? "btn btn-primary btn-sm" : "btn btn-ghost btn-sm"}
                      onClick={async () => {
                        try {
                          await resumeApi.recommend(selResume, r.dept_id);
                          toast.success(`已推荐到「${r.dept_name}」`);
                        } catch {}
                      }}
                    >
                      <ArrowRight size={14} /> 推荐到
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

function Person({ avatar, name, role }: { avatar: string; name: string; role: string }) {
  return (
    <div className="flex items-center gap-2">
      <div className="w-[25px] h-[25px] rounded-md bg-[#F6F8FC] border border-line flex items-center justify-center text-[10.5px] font-semibold text-text-2">
        {avatar}
      </div>
      <div>
        <b className="text-[12px] block font-semibold">{name}</b>
        <span className="text-[10px] text-text-3">{role}</span>
      </div>
    </div>
  );
}