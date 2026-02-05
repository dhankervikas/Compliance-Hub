import os

target_path = r"C:\Users\dhank\OneDrive\Documents\Compliance_Product\Frontend\src\components\Controls.js"

with open(target_path, 'r', encoding='utf-8') as f:
    content = f.read()

search_str = """                                  <h5 className="text-xs font-bold text-gray-700 uppercase mb-1">Recommendations</h5>
                                  <p className="text-sm text-gray-600">{assess.recommendations || "No recommendations."}</p>
                                </div>
                              </div>
                            </div>
                           )"""

replace_str = """                                  <h5 className="text-xs font-bold text-gray-700 uppercase mb-1">Recommendations</h5>
                                  <p className="text-sm text-gray-600">{assess.recommendations || "No recommendations."}</p>
                                </div>
                              </div>
                              <div className="mt-3 border-t border-purple-100 pt-3 flex justify-end">
                                <button 
                                  className="text-xs flex items-center gap-1 text-purple-600 hover:text-purple-800 font-medium"
                                  onClick={async (e) => {
                                     e.stopPropagation();
                                     if(window.confirm('Run a new AI assessment? This may take a few seconds.')) {
                                       // Optimistic UI update
                                       try {
                                         await assessmentService.triggerAnalysis(control.id);
                                         const data = await assessmentService.getForControl(control.id);
                                         setAssessments(prev => ({ ...prev, [control.id]: data }));
                                       } catch (err) {
                                         console.error(err);
                                         alert('Analysis failed');
                                       }
                                     }
                                  }}
                                >
                                  <Bot className="w-4 h-4" /> Re-run Analysis
                                </button>
                              </div>
                            </div>
                           )"""

if search_str in content:
    new_content = content.replace(search_str, replace_str)
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Injected Re-run button code.")
else:
    print("Could not find insertion point. File might be different than expected.")
    # Debug info
    print(f"Content length: {len(content)}")
    print(f"Search str length: {len(search_str)}")
