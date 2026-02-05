import api from "./api";

const assessmentService = {
  getForControl: async (controlId) => {
    const response = await api.get(`/assessments/control/${controlId}`);
    return response.data;
  },
  
  triggerAnalysis: async (controlId) => {
    const response = await api.post(`/assessments/analyze/${controlId}`);
    return response.data;
  }
};

export default assessmentService;