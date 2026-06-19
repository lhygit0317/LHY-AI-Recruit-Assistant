import { useEffect, useState } from "react";
import { Sparkles, Play } from "lucide-react";
import toast from "react-hot-toast";
import { analysisApi, posApi, resumeApi } from "@/api/client";
import type { AnalysisResult, Position, QuestionSet, Resume } from "@/api/types";
import { scoreColor, verdictText } from "@/lib/utils";

export default function Parse() {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [positions, setPositions] = useState<Position[]>([]);
  const [selResume, setSelResume] = useState("");
  const [selPos, setSelPos] = useState("");
  const [chan, setChan] = useState<"社招" | "校招">("社招");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [questions, setQuestions] = useState<QuestionSet | null>(null);
  const [qtab, setQtab] = useState<"专业" | "主管" | "资格">("专业");
  const [useAI, setUseAI] = useState(true);
  const [qLoading, setQLoading] = useState(false);

  useEffect(() => {
    resumeApi.list({ chan }).then((d) => {
      setResumes(d.items);
      if (d.items.length) setSelResume(d.items[0].id);
    });
    posApi.list({ chan, active_only: true }).then((d) => {
      setPositions(d);
      if (d.length) setSelPos(d[0].id);
    });
  }, [chan]);

  const run = async () => {
    if (!selResume || !selPos) {
      toast.error("请选择简历和岗位");
      return;
    }
    setLoading(true);
    setResult(null);
    setQuestions(null);
    try {
      const a = await analysisApi.match(selResume, selPos, useAI);
      setResult(a);
    } catch {} finally {
      setLoading(false);
    }
  };

  const genQuestions = async () => {
    if (!selResume || !selPos) return;
    setQLoading(true);
    try {
      const qs = await analysisApi.questions(selResume, selPos, useAI);
      setQuestions(qs);
      if (useAI) toast.success("AI 已生成面试题");
    } catch {} finally {
      setQLoading(false);
    }
  };

  const resume = resumes.find((r) => r.id === selResume);
  const position = positions.find((p) => p.id === selPos);

  return (
    <>
      <div className="mb-6">
        <h1 className="text-[23px] font-semibold tracking-tight flex items-center gap-3">
          简历解析
          <span className="tag tag-blue">JD + 隐性标签 智能匹配</span>
        </h1>
        <p className="text-text-2 mt-2 text-[13.5px] max-w-[760px]">
          选择简历库中已有简历或导入新简历，结合岗位 JD 与 HRBP 配置的隐性标签，自动判断适配度，并按需生成三轮面试题、导出 MD。
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
        {/* 左：选择 */}
        <div className="card card-pad">
          <div className="flex items-center gap-2 text-[13.5px] font-semibold mb-3.5">
            <div className="w-1.5 h-1.5 rounded-sm bg-blue" /> ① 选择简历与岗位
          </div>

          <div className="mt-4">
            <label className="block text-xs font-semibold text-text-2 mb-2">选择简历</label>
            <select
              className="input"
              value={selResume}
              onChange={(e) => setSelResume(e.target.value)}
            >
              {resumes.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name} · {r.pos} · {r.current_dept_name}
                </option>
              ))}
            </select>
          </div>

          <div className="mt-4">
            <label className="block text-xs font-semibold text-text-2 mb-2">目标岗位 JD</label>
            <select
              className="input"
              value={selPos}
              onChange={(e) => setSelPos(e.target.value)}
            >
              {positions.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.department_name} · {p.name}（{p.chan}）
                </option>
              ))}
            </select>
          </div>

          {/* AI 开关 */}
          <div className="mt-5 flex items-center justify-between p-3 bg-[#F6F8FC] border border-line rounded-md">
            <div>
              <div className="text-[13px] font-semibold flex items-center gap-1.5">
                <Sparkles size={14} className="text-violet" /> AI 增强
              </div>
              <div className="text-[11px] text-text-3 mt-0.5">
                开启后用 LLM 重写分析总结 + 生成面试题
              </div>
            </div>
            <button
              onClick={() => setUseAI(!useAI)}
              className={`relative w-10 h-5.5 rounded-full transition ${useAI ? "bg-blue" : "bg-line"}`}
              style={{ width: 40, height: 22 }}
            >
              <span
                className="absolute top-0.5 w-[18px] h-[18px] rounded-full bg-white shadow transition-all"
                style={{ left: useAI ? 20 : 2 }}
              />
            </button>
          </div>

          <button
            className="btn btn-primary w-full mt-4"
            onClick={run}
            disabled={!selResume || !selPos || loading}
          >
            <Play size={16} /> {loading ? (useAI ? "AI 解析中…" : "解析中…") : "开始解析"}
          </button>
        </div>

        {/* 右：结果 */}
        <div>
          {!result ? (
            <div className="card card-pad flex flex-col items-center justify-center min-h-[440px] text-text-3 border-dashed bg-[#F6F8FC]">
              <Sparkles size={42} className="mb-3.5 opacity-50" />
              <b className="text-text-2 font-semibold text-[14px]">解析结果将显示在这里</b>
              <span className="mt-1.5 text-[12.5px]">选择简历并选岗位后点击「开始解析」</span>
            </div>
          ) : (
            <div className="card card-pad">
              <div className="flex items-start justify-between gap-4 pb-5 border-b border-line">
                <div className="flex items-center gap-3.5">
                  <div className="w-12 h-12 rounded-[13px] bg-ink text-white flex items-center justify-center text-[18px] font-semibold">
                    {resume?.name[0]}
                  </div>
                  <div>
                    <h3 className="text-[17.5px] font-semibold flex items-center gap-2">
                      {resume?.name}
                      <span className="text-[10.5px] font-semibold px-2 py-0.5 rounded bg-blue-soft text-blue">
                        {resume?.chan}
                      </span>
                    </h3>
                    <div className="text-[12.5px] text-text-2 mt-1 flex gap-2 flex-wrap">
                      <span>意向：{position?.name}</span>
                      <span>·</span>
                      <span>当前部门：{resume?.current_dept_name}</span>
                    </div>
                    <div className="flex gap-1.5 flex-wrap mt-2">
                      {resume?.keywords.map((k) => (
                        <span key={k} className="text-[10.5px] font-medium px-1.5 py-0.5 rounded bg-blue-soft text-blue-dark">
                          {k}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3.5 flex-shrink-0">
                  <ScoreRing score={result.total} />
                  <div>
                    <div className="text-text-3 text-[10.5px] tracking-wider uppercase">系统判断</div>
                    <b className="block text-[15px] mt-0.5" style={{ color: scoreColor(result.total) }}>
                      {result.verdict}
                    </b>
                  </div>
                </div>
              </div>

              {/* 评分条 */}
              <div className="mt-5 grid gap-3.5">
                <BarRow label="技能匹配" value={result.skill} />
                <BarRow label="经验匹配" value={result.exp} />
                <BarRow label="隐性要求" value={result.implicit} />
              </div>

              {/* 命中/未命中 */}
              <div className="mt-4 grid grid-cols-2 gap-3">
                <div className="border border-line rounded-[11px] p-3.5 bg-[#F6F8FC]">
                  <div className="text-[11.5px] text-text-3 mb-2 font-semibold">技能关键词命中（vs JD）</div>
                  <div className="flex gap-1.5 flex-wrap">
                    {result.k_hit.map((k) => (
                      <span key={k} className="text-[11px] font-medium px-2 py-0.5 rounded bg-green-soft text-green">
                        ✓ {k}
                      </span>
                    ))}
                    {result.k_miss.map((k) => (
                      <span key={k} className="text-[11px] font-medium px-2 py-0.5 rounded bg-[#F0F2F6] text-text-3">
                        {k}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="border border-line rounded-[11px] p-3.5 bg-[#F6F8FC]">
                  <div className="text-[11.5px] text-text-3 mb-2 font-semibold">隐性标签命中（HRBP 配置）</div>
                  <div className="flex gap-1.5 flex-wrap">
                    {result.t_hit.map((k) => (
                      <span key={k} className="text-[11px] font-medium px-2 py-0.5 rounded bg-green-soft text-green">
                        ✓ {k}
                      </span>
                    ))}
                    {result.t_miss.map((k) => (
                      <span key={k} className="text-[11px] font-medium px-2 py-0.5 rounded bg-[#F0F2F6] text-text-3">
                        {k}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* 分析 */}
              <div
                className="mt-5 p-3.5 rounded-[11px] text-[13px] leading-relaxed flex gap-2.5"
                style={{
                  background: verdictText(result.total).cls === "tag-green" ? "#E3F5EA" :
                              verdictText(result.total).cls === "tag-amber" ? "#FBEEDA" : "#FBEBEA",
                  color: verdictText(result.total).cls === "tag-green" ? "#136e3c" :
                         verdictText(result.total).cls === "tag-amber" ? "#8a5108" : "#9c2c2c",
                }}
              >
                <div className="flex-1">
                  <b>分析：</b>技能命中 {result.k_hit.length}/{position?.keywords.length}，
                  隐性要求命中 {result.t_hit.length}/{position?.implicit.length} 项。
                  <div className="mt-2 text-[13px]">{result.summary}</div>
                </div>
                {useAI && (
                  <span className="flex-shrink-0 self-start pill tag-violet text-[10px]">AI</span>
                )}
              </div>

              {/* 面试题 */}
              <div className="mt-6">
                <div className="flex items-center gap-2 text-[13.5px] font-semibold mb-3.5">
                  <div className="w-1.5 h-1.5 rounded-sm bg-blue" />
                  面试题
                </div>
                {questions ? (
                  <>
                    <div className="flex items-center gap-3 mb-2.5">
                      <div className="flex gap-5 border-b border-line flex-1">
                        {(["专业", "主管", "资格"] as const).map((t) => (
                          <button
                            key={t}
                            className={`py-2 text-[13px] font-medium border-b-2 ${
                              qtab === t ? "text-text border-ink" : "text-text-3 border-transparent"
                            }`}
                            onClick={() => setQtab(t)}
                          >
                            {t}面试
                          </button>
                        ))}
                      </div>
                      {useAI && <span className="pill tag-violet text-[10px] flex-shrink-0">AI 生成</span>}
                    </div>
                    <div className="pt-4 grid gap-2.5">
                      {questions[qtab].map((q, i) => (
                        <div key={i} className="flex gap-3 p-3 bg-[#F6F8FC] border border-line rounded-[11px]">
                          <div className="font-mono text-[12px] font-bold text-blue flex-shrink-0 w-[22px]">
                            {String(i + 1).padStart(2, "0")}
                          </div>
                          <div className="text-[13.5px] leading-relaxed flex-1">
                            {q.q}
                            <span className="block mt-1 text-[11.5px] text-text-3">↳ {q.why}</span>
                          </div>
                          <span className="text-[10.5px] font-semibold px-2 py-0.5 rounded bg-white border border-line text-text-2 self-start flex-shrink-0">
                            {q.lvl}
                          </span>
                        </div>
                      ))}
                    </div>
                  </>
                ) : (
                  <div className="border border-dashed border-line rounded-[12px] p-6 text-center bg-[#F6F8FC]">
                    <p className="text-[13px] text-text-2 mb-3.5">面试题需点击生成（结合候选人与岗位 JD）</p>
                    <button className="btn btn-primary btn-sm" onClick={genQuestions} disabled={qLoading}>
                      <Sparkles size={14} /> {qLoading ? "生成中…" : useAI ? "AI 生成面试题" : "生成面试题"}
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

function BarRow({ label, value }: { label: string; value: number }) {
  const c = scoreColor(value);
  return (
    <div className="grid items-center gap-3.5" style={{ gridTemplateColumns: "118px 1fr 46px" }}>
      <div className="text-[12.5px] text-text-2">{label}</div>
      <div className="bar-track">
        <div className="bar-fill" style={{ width: `${value}%`, background: c }} />
      </div>
      <div className="font-mono text-[13px] font-semibold text-right" style={{ color: c }}>{value}</div>
    </div>
  );
}

function ScoreRing({ score }: { score: number }) {
  const c = scoreColor(score);
  const radius = 37;
  const circ = 2 * Math.PI * radius;
  const offset = circ * (1 - score / 100);
  return (
    <div className="relative w-[88px] h-[88px] flex-shrink-0">
      <svg width="88" height="88" style={{ transform: "rotate(-90deg)" }}>
        <circle cx="44" cy="44" r={radius} fill="none" stroke="#E4E8F0" strokeWidth="8" />
        <circle
          cx="44" cy="44" r={radius} fill="none" stroke={c} strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={`${circ * score / 100} ${circ}`}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <b className="font-mono text-[25px] font-bold leading-none" style={{ color: c }}>{score}</b>
        <small className="text-[10px] text-text-3 mt-0.5">匹配度</small>
      </div>
    </div>
  );
}