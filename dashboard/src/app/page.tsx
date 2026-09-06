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
} from "recharts";
import { AlertCircle, CheckCircle2, Database, HardDrive } from "lucide-react";

export default function Dashboard() {
  const [data, setData] = useState<BenchmarkResult[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/results/");
        if (!res.ok) throw new Error("Failed to fetch");
        const json = await res.json();
        // Sort by oldest first for time series
        setData(json.reverse());
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  // Prepare data for the chart (Execution time line + Spill points)
  const chartData = data.map((d) => ({
    time: new Date(d.timestamp).toLocaleTimeString(),
    execution_time_ms: d.execution_time_ms,
    spilled: d.spilled_to_disk ? d.execution_time_ms : null,
    query_name: d.query_name,
  }));

  const totalRuns = data.length;
  const spillCount = data.filter((d) => d.spilled_to_disk).length;

  return (
    <main className="min-h-screen bg-slate-50 p-8 text-slate-900">
      <div className="max-w-7xl mx-auto space-y-8">
        
        <header className="border-b border-slate-200 pb-5">
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">
            Query Performance Benchmarker
          </h1>
          <p className="text-slate-500 mt-2">
            Real-time monitoring of disk spills under strict memory constraints (256MB RAM / 4MB work_mem).
          </p>
        </header>

        {loading ? (
          <div className="animate-pulse flex space-x-4">
            <div className="flex-1 space-y-4 py-1">
              <div className="h-4 bg-slate-200 rounded w-3/4"></div>
              <div className="space-y-2">
                <div className="h-4 bg-slate-200 rounded"></div>
                <div className="h-4 bg-slate-200 rounded w-5/6"></div>
              </div>
            </div>
          </div>
        ) : (
          <>
            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 flex items-center space-x-4">
                <div className="p-3 bg-blue-100 text-blue-600 rounded-lg">
                  <Database size={24} />
                </div>
                <div>
                  <p className="text-sm font-medium text-slate-500">Total Queries Run</p>
                  <p className="text-2xl font-bold">{totalRuns}</p>
                </div>
              </div>

              <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 flex items-center space-x-4">
                <div className="p-3 bg-red-100 text-red-600 rounded-lg">
                  <HardDrive size={24} />
                </div>
                <div>
                  <p className="text-sm font-medium text-slate-500">Disk Spills Detected</p>
                  <p className="text-2xl font-bold">{spillCount}</p>
                </div>
              </div>

              <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 flex items-center space-x-4">
                <div className="p-3 bg-slate-100 text-slate-600 rounded-lg">
                  <AlertCircle size={24} />
                </div>
                <div>
                  <p className="text-sm font-medium text-slate-500">Spill Rate</p>
                  <p className="text-2xl font-bold">
                    {totalRuns > 0 ? ((spillCount / totalRuns) * 100).toFixed(1) : 0}%
                  </p>
                </div>
              </div>
            </div>

            {/* Chart */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
              <h2 className="text-lg font-semibold mb-6">Execution Time vs. Disk Spills</h2>
              <div className="h-96">
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart data={chartData} margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="time" tick={{ fontSize: 12, fill: '#64748b' }} />
                    <YAxis 
                      label={{ value: 'Execution Time (ms)', angle: -90, position: 'insideLeft', fill: '#64748b' }} 
                      tick={{ fontSize: 12, fill: '#64748b' }}
                    />
                    <Tooltip 
                      contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                    />
                    <Legend />
                    <Line 
                      type="monotone" 
                      dataKey="execution_time_ms" 
                      name="Execution Time (ms)" 
                      stroke="#3b82f6" 
                      strokeWidth={2}
                      dot={false}
                    />
                    <Scatter 
                      dataKey="spilled" 
                      name="Disk Spill Event" 
                      fill="#ef4444" 
                      shape="circle" 
                    />
                  </ComposedChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Table */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
              <div className="p-6 border-b border-slate-200">
                <h2 className="text-lg font-semibold">Recent Benchmark Logs</h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                  <thead className="text-xs text-slate-500 bg-slate-50 uppercase border-b border-slate-200">
                    <tr>
                      <th className="px-6 py-4 font-medium">Timestamp</th>
                      <th className="px-6 py-4 font-medium">Query Name</th>
                      <th className="px-6 py-4 font-medium text-right">Exec Time (ms)</th>
                      <th className="px-6 py-4 font-medium text-center">Spill Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[...data].reverse().map((row) => (
                      <tr key={row.id} className="border-b border-slate-100 last:border-0 hover:bg-slate-50/50">
                        <td className="px-6 py-4 text-slate-600">
                          {new Date(row.timestamp).toLocaleString()}
                        </td>
                        <td className="px-6 py-4 font-medium text-slate-900">
                          {row.query_name}
                        </td>
                        <td className="px-6 py-4 text-right tabular-nums">
                          {row.execution_time_ms.toFixed(2)}
                        </td>
                        <td className="px-6 py-4 flex justify-center">
                          {row.spilled_to_disk ? (
                            <span className="inline-flex items-center space-x-1 px-2.5 py-1 bg-red-50 text-red-700 rounded-full text-xs font-medium">
                              <HardDrive size={12} />
                              <span>Spilled</span>
                            </span>
                          ) : (
                            <span className="inline-flex items-center space-x-1 px-2.5 py-1 bg-green-50 text-green-700 rounded-full text-xs font-medium">
                              <CheckCircle2 size={12} />
                              <span>In-Memory</span>
                            </span>
                          )}
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
