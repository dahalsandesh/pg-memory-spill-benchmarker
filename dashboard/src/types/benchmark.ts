export interface BenchmarkResult {
  id: number;
  query_name: string;
  execution_time_ms: number;
  ram_allocated_mb: number;
  spilled_to_disk: boolean;
  spill_type: string;
  sort_space_used_kb: number;
  hash_batches: number;
  temp_read_blocks: number;
  temp_written_blocks: number;
  work_mem_kb: number;
  timestamp: string;
}
