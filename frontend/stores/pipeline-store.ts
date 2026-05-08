import { create } from "zustand";
import { apiClient } from "@/services/api-client";

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
      // In a real implementation, this would hit the FastAPI backend
      // const response = await apiClient.get(`/pipelines/${activePipelineId}`);
      // set({ progress: response.data.progress, status: response.data.status, chunks: response.data.chunks });
      
      // For MVP UI mock
      set((state) => ({
        progress: Math.min(state.progress + 5, 100),
        status: state.progress >= 95 ? "completed" : "running"
      }));
    } catch (error) {
      console.error("Failed to fetch pipeline status", error);
    }
  },

  startPolling: () => {
    if (pollingInterval) clearInterval(pollingInterval);
    pollingInterval = setInterval(() => {
      get().fetchPipelineStatus();
    }, 3000); // Poll every 3 seconds for MVP
  },

  stopPolling: () => {
    if (pollingInterval) {
      clearInterval(pollingInterval);
      pollingInterval = null;
    }
  }
}));
