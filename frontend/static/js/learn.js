// Learn page specific JavaScript functionality
// Uses shared utilities from learning.js

// Enhanced preview function with detailed module information
function previewModule(moduleId) {
  console.log('Previewing module:', moduleId);
  
  const moduleNames = {
    1: "ISL Alphabet & Fingerspelling",
    2: "Numbers & Mathematical Concepts", 
    3: "Family & Relationships",
    4: "Colors, Shapes & Objects",
    5: "Time & Calendar Concepts",
    6: "Basic Grammar & Sentence Structure",
    7: "Daily Activities & Routines",
    8: "Emotions & Feelings",
    9: "Places & Directions",
    10: "Food & Health",
    11: "Education & Work",
    12: "Advanced Grammar & Discourse"
  };
  
  const moduleName = moduleNames[moduleId] || 'Module ' + moduleId;
  
  // Show detailed preview information
  alert(`Preview: ${moduleName}\n\nThis module includes:\n• HD video lessons\n• Interactive exercises\n• Practice sessions\n• Assessment quiz\n• Progress tracking\n\nClick "Start Module" to begin learning!`);
}

// Enhanced certification info function
function showCertificationInfo() {
  // Use the shared utility function from learning.js
  if (window.LearningUtils && window.LearningUtils.showCertificationInfo) {
    window.LearningUtils.showCertificationInfo();
  } else {
    // Fallback if learning.js is not loaded
    alert(`ISLRTC Certification Program\n\n📜 Foundation Level (Modules 1-6):\n• 40-60 hours of study\n• Basic ISL proficiency\n• Government recognized certificate\n\n🏆 Intermediate Level (Modules 7-12):\n• 50-70 hours of study\n• Advanced communication skills\n• Professional qualification\n\n👨‍🏫 Instructor Qualification:\n• Additional training program\n• Teaching methodology\n• Certification to teach ISL\n\nAll certificates are issued by ISLRTC and recognized by Government of India institutions.`);
  }
}