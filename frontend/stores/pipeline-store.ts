import { create } from "zustand";
import { pipelineService } from "@/services/pipeline-service";

interface PipelineState {
  activePipelineId: string | null;
  progress: number;
  status: "idle" | "running" | "paused" | "failed" | "completed";
  chunks: any[];
  setActivePipeline: (id: string) => void;
  fetchPipelineStatus: () => Promise<void>;
  startPolling: () => void;
  stopPolling: () => void;
}

let pollingInterval: NodeJS.Timeout | null = null;

export const usePipelineStore = create<PipelineState>((set, get) => ({
  activePipelineId: null,
  progress: 0,
  status: "idle",
  chunks: [],

  setActivePipeline: (id) => set({ activePipelineId: id }),

  fetchPipelineStatus: async () => {
    const { activePipelineId } = get();
    if (!activePipelineId) return;

    try {
      // Connect to the real backend
      const pipeline = await pipelineService.getPipeline(activePipelineId);
      const chunkData = await pipelineService.getPipelineChunks(activePipelineId);
      
      let newProgress = 0;
      if (pipeline.total_chunks > 0) {
        newProgress = Math.round((pipeline.completed_chunks / pipeline.total_chunks) * 100);
      }

      set({ 
        progress: newProgress, 
        status: pipeline.status, 
        chunks: chunkData.items || [] 
      });
    } catch (error) {
      console.error("Failed to fetch pipeline status", error);
    }
  },

  startPolling: () => {
    if (pollingInterval) clearInterval(pollingInterval);
    // Initial fetch
    get().fetchPipelineStatus();
    // Poll every 3 seconds
    pollingInterval = setInterval(() => {
      get().fetchPipelineStatus();
    }, 3000);
  },

  stopPolling: () => {
    if (pollingInterval) {
      clearInterval(pollingInterval);
      pollingInterval = null;
    }
  }
}));
