import { apiClient } from "./api-client";

export const pipelineService = {
  getPipeline: async (id: string) => {
    const response = await apiClient.get(`/pipelines/${id}`);
    return response.data;
  },

  getPipelineChunks: async (id: string, page = 1, size = 100) => {
    const response = await apiClient.get(`/pipelines/${id}/chunks`, {
      params: { page, size }
    });
    return response.data;
  },

  getArtifact: async (chunkId: string) => {
    const response = await apiClient.get(`/chunks/${chunkId}/artifact`);
    return response.data;
  },

  startPipeline: async (id: string) => {
    const response = await apiClient.post(`/pipelines/${id}/start`);
    return response.data;
  },

  getDashboardStats: async () => {
    const response = await apiClient.get(`/system/stats`);
    return response.data;
  }
};
