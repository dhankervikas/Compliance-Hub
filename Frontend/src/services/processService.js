import api from "./api";

const processService = {
  getAll: async () => {
    const response = await api.get("/processes/");
    return response.data;
  },

  create: async (processData) => {
    const response = await api.post("/processes/", processData);
    return response.data;
  },

  mapControls: async (subProcessId, controlIds) => {
    const response = await api.post(`/processes/subprocess/${subProcessId}/map-controls`, {
      control_ids: controlIds
    });
    return response.data;
  }
};

export default processService;
