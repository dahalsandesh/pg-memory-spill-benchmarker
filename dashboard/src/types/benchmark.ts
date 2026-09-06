export interface BenchmarkResult {
  id: number;
  query_name: string;
  execution_time_ms: number;
  ram_allocated_mb: number;
  spilled_to_disk: boolean;
  timestamp: string;
}
