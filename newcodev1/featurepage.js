import React from 'react';
import './FeaturesPage.css';

const FeaturesPage = ({ onClose, version }) => {
  const features = [
    {
      category: "🎯 Core Features",
      items: [
        "Dynamic KEDB Search & Suggestions",
        "AI-Powered KEDB Generation", 
        "Real-time Content Editing",
        "Excel File Processing Integration",
        "DOCX Document Export"
      ]
    },
    {
      category: "🔧 Technical Features", 
      items: [
        "RESTful API Integration",
        "Responsive Design (Mobile & Desktop)",
        "Loading States & Error Handling",
        "Persistent Input Section",
        "State Management without Unnecessary API Calls"
      ]
    },
    {
      category: "💡 User Experience",
      items: [
        "Interactive Tooltip Help System",
        "One-Click KEDB Content Display", 
        "Cancel Navigation (No API Calls)",
        "Version Information & Features Link",
        "Professional Styling & Animations"
      ]
    },
    {
      category: "📱 Interface Features",
      items: [
        "Suggested KEDB List with Recommendations",
        "Expandable Editor with Live Preview",
        "Download Progress Indicators", 
        "Hover Effects & Visual Feedback",
        "Clean Material Design Inspired UI"
      ]
    },
    {
      category: "🚀 Performance Features",
      items: [
        "Optimized Re-rendering",
        "Efficient State Management",
        "Lazy Loading Components", 
        "Minimal Bundle Size",
        "Fast API Response Handling"
      ]
    },
    {
      category: "🔒 Data Features",
      items: [
        "Secure API Communication",
        "Local State Preservation",
        "Content Validation & Sanitization",
        "Error Recovery Mechanisms",
        "Data Export Security"
      ]
    }
  ];

  return (
    <div className="features-page">
      <div className="features-header">
        <div className="features-title">
          <h1>🚀 KEDB Draft Generator - Live Features</h1>
          <span className="version-badge">Version {version}</span>
        </div>
        <button className="close-btn" onClick={onClose}>
          ✕ Back to App
        </button>
      </div>

      <div className="features-content">
        <div className="features-intro">
          <p>
            🎉 Welcome to the comprehensive features list of the KEDB Draft Generator App! 
            This tool is designed to streamline incident resolution documentation with 
            powerful automation and user-friendly interfaces.
          </p>
        </div>

        <div className="features-grid">
          {features.map((category, index) => (
            <div key={index} className="feature-category">
              <h3 className="category-title">{category.category}</h3>
              <ul className="feature-list">
                {category.items.map((feature, featureIndex) => (
                  <li key={featureIndex} className="feature-item">
                    ✅ {feature}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="features-footer">
          <div className="update-info">
            <h4>📅 Latest Updates</h4>
            <ul>
              <li>✨ Added working tooltip help system</li>
              <li>🔗 Version information with features link</li>
              <li>⚡ Enhanced API integration</li>
              <li>📱 Improved responsive design</li>
              <li>🎨 Professional UI enhancements</li>
            </ul>
          </div>
          
          <div className="tech-stack">
            <h4>🛠️ Technology Stack</h4>
            <div className="tech-tags">
              <span className="tech-tag">React 18+</span>
              <span className="tech-tag">JavaScript ES6+</span>
              <span className="tech-tag">CSS3</span>
              <span className="tech-tag">REST APIs</span>
              <span className="tech-tag">XLSX</span>
              <span className="tech-tag">DOCX</span>
              <span className="tech-tag">File-Saver</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FeaturesPage;
