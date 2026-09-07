"use client";

import { useEffect, useState } from "react";
import { BenchmarkResult } from "@/types/benchmark";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Scatter,
  ComposedChart,
  Bar,
  AreaChart,
  Area,
} from "recharts";
import { AlertCircle, CheckCircle2, Database, HardDrive, Cpu, Activity } from "lucide-react";

export default function Dashboard() {
  const [data, setData] = useState<BenchmarkResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/results/";
        const res = await fetch(apiUrl);
        if (!res.ok) throw new Error("Failed to fetch data from Metrics API");
        const json = await res.json();
        setData(json.reverse());
        setError(null);
      } catch (err: any) {
        console.error(err);
        setError(err.message || "Failed to connect to backend");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const chartData = data.map((d) => ({
    time: new Date(d.timestamp).toLocaleTimeString(),
    execution_time_ms: d.execution_time_ms,
    spilled: d.spilled_to_disk ? d.execution_time_ms : null,
    query_name: d.query_name,
    temp_blocks: d.temp_written_blocks + d.temp_read_blocks,
    sort_space: d.sort_space_used_kb,
  }));

  const totalRuns = data.length;
  const spillCount = data.filter((d) => d.spilled_to_disk).length;
  const avgTempBlocks = totalRuns > 0 ? Math.round(data.reduce((acc, d) => acc + d.temp_read_blocks + d.temp_written_blocks, 0) / totalRuns) : 0;
  const avgSortSpace = totalRuns > 0 ? Math.round(data.reduce((acc, d) => acc + d.sort_space_used_kb, 0) / totalRuns) : 0;

  return (
    <main className="min-h-screen bg-[#09090b] text-zinc-100 p-8 font-sans selection:bg-indigo-500/30">
      <div className="max-w-7xl mx-auto space-y-8">
        
        <header className="border-b border-zinc-800 pb-6 flex justify-between items-end">
          <div>
            <div className="flex items-center space-x-3 mb-2">
              <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></div>
              <span className="text-xs font-mono text-emerald-500 tracking-wider uppercase">Live Telemetry</span>
            </div>
            <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
              Flow-Centric Query Pipeline Telemetry
            </h1>
            <p className="text-zinc-400 mt-2 text-sm max-w-2xl leading-relaxed">
              Empirical evaluation of pipeline barrier degradation (Sort & Hash operator spills) under strict memory constraints (work_mem: 2MB).
            </p>
          </div>
        </header>

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-3 rounded-lg flex items-center space-x-3">
            <AlertCircle size={18} />
            <p className="text-sm font-medium">{error}</p>
          </div>
        )}

        {loading ? (
          <div className="animate-pulse flex space-x-4">
            <div className="flex-1 space-y-4 py-1">
              <div className="h-4 bg-zinc-800 rounded w-3/4"></div>
              <div className="space-y-2">
                <div className="h-4 bg-zinc-800 rounded"></div>
                <div className="h-4 bg-zinc-800 rounded w-5/6"></div>
              </div>
            </div>
          </div>
        ) : (
          <>
            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-zinc-900/50 backdrop-blur-xl p-5 rounded-xl border border-zinc-800/50 flex flex-col justify-between hover:border-zinc-700 transition-colors">
                <div className="flex justify-between items-start mb-4">
                  <div className="p-2 bg-indigo-500/10 text-indigo-400 rounded-lg">
                    <Activity size={20} />
                  </div>
                </div>
                <div>
                  <p className="text-xs font-medium text-zinc-500 uppercase tracking-wider">Total Executions</p>
                  <p className="text-2xl font-bold text-zinc-100 mt-1">{totalRuns}</p>
                </div>
              </div>

              <div className="bg-zinc-900/50 backdrop-blur-xl p-5 rounded-xl border border-zinc-800/50 flex flex-col justify-between hover:border-zinc-700 transition-colors">
                <div className="flex justify-between items-start mb-4">
                  <div className="p-2 bg-rose-500/10 text-rose-400 rounded-lg">
                    <HardDrive size={20} />
                  </div>
                </div>
                <div>
                  <p className="text-xs font-medium text-zinc-500 uppercase tracking-wider">Spill Events</p>
                  <div className="flex items-baseline space-x-2 mt-1">
                    <p className="text-2xl font-bold text-zinc-100">{spillCount}</p>
                    <p className="text-xs font-medium text-rose-400">
                      ({totalRuns > 0 ? ((spillCount / totalRuns) * 100).toFixed(1) : 0}%)
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-zinc-900/50 backdrop-blur-xl p-5 rounded-xl border border-zinc-800/50 flex flex-col justify-between hover:border-zinc-700 transition-colors">
                <div className="flex justify-between items-start mb-4">
                  <div className="p-2 bg-amber-500/10 text-amber-400 rounded-lg">
                    <Database size={20} />
                  </div>
                </div>
                <div>
                  <p className="text-xs font-medium text-zinc-500 uppercase tracking-wider">Avg Disk I/O (Blocks)</p>
                  <p className="text-2xl font-bold text-zinc-100 mt-1">{avgTempBlocks}</p>
                </div>
              </div>

              <div className="bg-zinc-900/50 backdrop-blur-xl p-5 rounded-xl border border-zinc-800/50 flex flex-col justify-between hover:border-zinc-700 transition-colors">
                <div className="flex justify-between items-start mb-4">
                  <div className="p-2 bg-emerald-500/10 text-emerald-400 rounded-lg">
                    <Cpu size={20} />
                  </div>
                </div>
                <div>
                  <p className="text-xs font-medium text-zinc-500 uppercase tracking-wider">Avg Sort Space</p>
                  <div className="flex items-baseline space-x-1 mt-1">
                    <p className="text-2xl font-bold text-zinc-100">{avgSortSpace}</p>
                    <p className="text-xs font-medium text-zinc-500">KB</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Performance Chart */}
              <div className="bg-zinc-900/50 backdrop-blur-xl p-6 rounded-xl border border-zinc-800/50">
                <h2 className="text-sm font-semibold text-zinc-300 mb-6 flex items-center">
                  <Activity size={16} className="mr-2 text-indigo-400" />
                  Execution Latency vs. Spills
                </h2>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart data={chartData} margin={{ top: 10, right: 10, bottom: 0, left: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
                      <XAxis dataKey="time" tick={{ fontSize: 11, fill: '#71717a' }} tickLine={false} axisLine={false} />
                      <YAxis tick={{ fontSize: 11, fill: '#71717a' }} tickLine={false} axisLine={false} tickFormatter={(val) => `${val}ms`} />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '8px', fontSize: '12px', color: '#e4e4e7' }}
                        itemStyle={{ color: '#e4e4e7' }}
                      />
                      <Line type="monotone" dataKey="execution_time_ms" name="Execution (ms)" stroke="#6366f1" strokeWidth={2} dot={false} />
                      <Scatter dataKey="spilled" name="Spill Event" fill="#f43f5e" shape="circle" />
                    </ComposedChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* I/O Chart */}
              <div className="bg-zinc-900/50 backdrop-blur-xl p-6 rounded-xl border border-zinc-800/50">
                <h2 className="text-sm font-semibold text-zinc-300 mb-6 flex items-center">
                  <HardDrive size={16} className="mr-2 text-rose-400" />
                  Pipeline Breaker I/O Footprint
                </h2>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={chartData} margin={{ top: 10, right: 10, bottom: 0, left: 0 }}>
                      <defs>
                        <linearGradient id="colorTemp" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3}/>
                          <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
                      <XAxis dataKey="time" tick={{ fontSize: 11, fill: '#71717a' }} tickLine={false} axisLine={false} />
                      <YAxis tick={{ fontSize: 11, fill: '#71717a' }} tickLine={false} axisLine={false} />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '8px', fontSize: '12px' }}
                      />
                      <Area type="monotone" dataKey="temp_blocks" name="I/O Blocks" stroke="#f59e0b" fillOpacity={1} fill="url(#colorTemp)" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* Table */}
            <div className="bg-zinc-900/50 backdrop-blur-xl rounded-xl border border-zinc-800/50 overflow-hidden">
              <div className="p-5 border-b border-zinc-800/80">
                <h2 className="text-sm font-semibold text-zinc-300">Detailed Execution Traces</h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                  <thead className="text-xs text-zinc-500 uppercase bg-zinc-900/50 border-b border-zinc-800">
                    <tr>
                      <th className="px-5 py-3 font-medium tracking-wider">Timestamp</th>
                      <th className="px-5 py-3 font-medium tracking-wider">Query Name</th>
                      <th className="px-5 py-3 font-medium tracking-wider text-right">Exec (ms)</th>
                      <th className="px-5 py-3 font-medium tracking-wider text-center">Spill Type</th>
                      <th className="px-5 py-3 font-medium tracking-wider text-right">Sort (KB)</th>
                      <th className="px-5 py-3 font-medium tracking-wider text-right">I/O Blks</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-800/50">
                    {[...data].reverse().map((row) => (
                      <tr key={row.id} className="hover:bg-zinc-800/20 transition-colors">
                        <td className="px-5 py-3 text-zinc-400 font-mono text-xs">
                          {new Date(row.timestamp).toLocaleTimeString()}
                        </td>
                        <td className="px-5 py-3 font-medium text-zinc-200">
                          {row.query_name}
                        </td>
                        <td className="px-5 py-3 text-right text-indigo-300 font-mono">
                          {row.execution_time_ms.toFixed(1)}
                        </td>
                        <td className="px-5 py-3 flex justify-center">
                          {row.spilled_to_disk ? (
                            <span className="inline-flex items-center space-x-1.5 px-2 py-0.5 bg-rose-500/10 text-rose-400 rounded-md text-[11px] font-medium border border-rose-500/20 uppercase tracking-wider">
                              <span>{row.spill_type.replace('_', ' ')}</span>
                            </span>
                          ) : (
                            <span className="inline-flex items-center space-x-1.5 px-2 py-0.5 bg-emerald-500/10 text-emerald-400 rounded-md text-[11px] font-medium border border-emerald-500/20 uppercase tracking-wider">
                              <span>In-Memory</span>
                            </span>
                          )}
                        </td>
                        <td className="px-5 py-3 text-right text-zinc-400 font-mono">
                          {row.sort_space_used_kb > 0 ? row.sort_space_used_kb : '-'}
                        </td>
                        <td className="px-5 py-3 text-right text-amber-300 font-mono">
                          {(row.temp_read_blocks + row.temp_written_blocks) || '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </div>
    </main>
  );
}
